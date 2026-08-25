import os
import sys
import json
import base64
import importlib.util
from unittest.mock import MagicMock

os.environ["UPLOAD_BUCKET"] = "test-bucket"
os.environ["AWS_ENDPOINT_URL"] = "http://localhost:4566"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

spec = importlib.util.spec_from_file_location(
    "upload_main",
    "lambda/upload/main.py"
)
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)


def test_upload_handler():
    main.s3 = MagicMock()

    image_content = b"test-image"

    event = {
        "body": json.dumps({
            "filename": "test.jpg",
            "content": base64.b64encode(image_content).decode()
        })
    }

    response = main.handler(event, None)

    assert response["statusCode"] == 201

    body = json.loads(response["body"])

    assert body["message"] == "Image uploaded successfully"
    assert body["key"].startswith("uploads/")
    assert body["key"].endswith("-test.jpg")

    main.s3.put_object.assert_called_once()

    call = main.s3.put_object.call_args.kwargs

    assert call["Bucket"] == "test-bucket"
    assert call["Body"] == image_content