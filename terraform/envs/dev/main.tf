
## Deploying S3 Bucket 

module "s3" {
  source = "../../modules/s3"

  upload_bucket_name    = "serverless-image-pipeline-uploads"
  processed_bucket_name = "serverless-image-pipeline-processed"

}

## Deploying SQS 

module "sqs" {
  source = "../../modules/sqs"

  queue_name = "serverless-image-pipeline"
}

## Deploying DynamoDB 

module "dynamodb" {
  source = "../../modules/dynamodb"

  table_name = "serverless-image-pipeline-images"
}


module "iam" {
  source = "../../modules/iam"

  project_name         = "serverless-image-pipeline"
  upload_bucket_arn    = module.s3.upload_bucket_arn
  processed_bucket_arn = module.s3.processed_bucket_arn
  dynamodb_table_arn   = module.dynamodb.table_arn
  queue_arn            = module.sqs.queue_arn
}

module "upload_lambda" {
  source = "../../modules/lambda"

  function_name = "serverless-image-pipeline-upload"
  source_dir    = "${path.root}/../../../lambda/upload"
  role_arn      = module.iam.upload_lambda_role_arn
  handler       = "main.handler"

  environment_variables = {
    UPLOAD_BUCKET    = module.s3.upload_bucket_name
    AWS_ENDPOINT_URL = "http://localhost.floci.io:4566"
  }
}

module "processor_lambda" {
  source = "../../modules/lambda"

  function_name = "serverless-image-pipeline-processor"
  source_dir    = "${path.root}/../../../lambda/processor"
  role_arn      = module.iam.processor_lambda_role_arn
  handler       = "main.handler"


  environment_variables = {
    UPLOAD_BUCKET    = module.s3.upload_bucket_name
    PROCESSED_BUCKET = module.s3.processed_bucket_name
    DYNAMODB_TABLE   = module.dynamodb.table_name
    AWS_ENDPOINT_URL = "http://localhost.floci.io:4566"
  }
}

resource "aws_s3_bucket_notification" "uploads" {
  bucket = module.s3.upload_bucket_name

  queue {
    queue_arn = module.sqs.queue_arn
    events    = ["s3:ObjectCreated:*"]
  }

  depends_on = [
    aws_sqs_queue_policy.allow_s3
  ]
}

resource "aws_sqs_queue_policy" "allow_s3" {
  queue_url = module.sqs.queue_url

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "s3.amazonaws.com"
        }

        Action   = "sqs:SendMessage"
        Resource = module.sqs.queue_arn

        Condition = {
          ArnEquals = {
            "aws:SourceArn" = module.s3.upload_bucket_arn
          }
        }
      }
    ]
  })
}

resource "aws_lambda_event_source_mapping" "processor_sqs" {
  event_source_arn = module.sqs.queue_arn
  function_name    = module.processor_lambda.function_arn
  batch_size       = 1

  depends_on = [
    module.processor_lambda,
    module.sqs
  ]
}


module "apigateway" {
  source = "../../modules/apigateway"

  api_name            = "serverless-image-pipeline-api"
  lambda_function_name = module.upload_lambda.function_name
  lambda_invoke_arn    = module.upload_lambda.invoke_arn
}



