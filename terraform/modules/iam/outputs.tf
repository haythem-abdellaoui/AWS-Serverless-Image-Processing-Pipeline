output "upload_lambda_role_arn" {
  value = aws_iam_role.upload_lambda.arn
}

output "processor_lambda_role_arn" {
  value = aws_iam_role.processor_lambda.arn
}