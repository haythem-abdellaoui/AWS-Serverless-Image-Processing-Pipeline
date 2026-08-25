import os
import sys
import json
import importlib.util
from io import BytesIO
from unittest.mock import MagicMock
from PIL import Image

os.environ["UPLOAD_BUCKET"] = "uploads"
os.environ["PROCESSED_BUCKET"] = "processed"
os.environ["DYNAMODB_TABLE"] = "images"
os.environ["AWS_ENDPOINT_URL"] = "http://localhost:4566"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

spec = importlib.util.spec_from_file_location(
    "processor_main",
    "lambda/processor/main.py"
)
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)


def test_processor_handler():
    image = Image.new("RGB", (100, 100), "red")

    image_data = BytesIO()
    image.save(image_data, format="JPEG")
    image_data.seek(0)

    main.s3 = MagicMock()
    main.table = MagicMock()

    main.s3.get_object.return_value = {
        "Body": image_data
    }

    event = {
        "Records": [
            {
                "body": json.dumps({
                    "Records": [
                        {
                            "s3": {
                                "bucket": {
                                    "name": "uploads"
                                },
                                "object": {
                                    "key": "uploads/test.jpg"
                                }
                            }
                        }
                    ]
                })
            }
        ]
    }

    response = main.handler(event, None)

    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert body["message"] == "Image processing completed"

    main.s3.get_object.assert_called_once_with(
        Bucket="uploads",
        Key="uploads/test.jpg"
    )

    main.s3.put_object.assert_called_once()

    item = main.table.put_item.call_args.kwargs["Item"]

    assert item["filename"] == "test.jpg"
    assert item["status"] == "COMPLETED"
    assert item["original_key"] == "uploads/test.jpg"
    assert item["processed_key"].startswith("processed/")