import json
import os
import uuid
import boto3
from io import BytesIO
from PIL import Image

s3 = boto3.client(
    "s3",
    endpoint_url=os.environ.get("AWS_ENDPOINT_URL")
)

dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url=os.environ.get("AWS_ENDPOINT_URL")
)

UPLOAD_BUCKET = os.environ["UPLOAD_BUCKET"]
PROCESSED_BUCKET = os.environ["PROCESSED_BUCKET"]
DYNAMODB_TABLE = os.environ["DYNAMODB_TABLE"]

table = dynamodb.Table(DYNAMODB_TABLE)


def handler(event, context):
    for record in event["Records"]:
        body = json.loads(record["body"])
        s3_event = body["Records"][0]

        bucket = s3_event["s3"]["bucket"]["name"]
        key = s3_event["s3"]["object"]["key"]

        image_id = str(uuid.uuid4())

        try:
            response = s3.get_object(
                Bucket=bucket,
                Key=key
            )

            image_data = response["Body"].read()

            image = Image.open(BytesIO(image_data))
            image.thumbnail((300, 300))

            output = BytesIO()
            if image.mode == "RGBA":
                image = image.convert("RGB")

            image.save(output, format="JPEG")
            output.seek(0)

            filename = os.path.basename(key)
            processed_key = f"processed/{image_id}-{filename}"

            s3.put_object(
                Bucket=PROCESSED_BUCKET,
                Key=processed_key,
                Body=output.getvalue(),
                ContentType="image/jpeg"
            )

            table.put_item(
                Item={
                    "image_id": image_id,
                    "filename": filename,
                    "status": "COMPLETED",
                    "original_key": key,
                    "processed_key": processed_key
                }
            )

            print(f"Processed {key} -> {processed_key}")

        except Exception as error:
            table.put_item(
                Item={
                    "image_id": image_id,
                    "filename": os.path.basename(key),
                    "status": "FAILED",
                    "original_key": key,
                    "error": str(error)
                }
            )

            raise

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Image processing completed"
        })
    }