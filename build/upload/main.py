import json
import os
import uuid
import base64
import boto3

s3 = boto3.client("s3", endpoint_url=os.environ.get("AWS_ENDPOINT_URL"))

BUCKET = os.environ["UPLOAD_BUCKET"]


def handler(event, context):
    body = json.loads(event["body"])

    filename = body["filename"]
    content = base64.b64decode(body["content"])

    key = f"uploads/{uuid.uuid4()}-{filename}"

    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=content
    )

    return {
        "statusCode": 201,
        "body": json.dumps({
            "message": "Image uploaded successfully",
            "key": key
        })
    }