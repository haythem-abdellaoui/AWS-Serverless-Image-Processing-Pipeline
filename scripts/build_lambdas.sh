#!/bin/bash

set -e

rm -rf build
mkdir -p build/upload build/processor

cp lambda/upload/main.py build/upload/

docker run --rm \
  --platform linux/amd64 \
  --entrypoint /bin/bash \
  -v "$PWD/build/processor":/var/task \
  public.ecr.aws/lambda/python:3.12 \
  -c "pip install --no-cache-dir Pillow boto3 -t /var/task"

cp lambda/processor/main.py build/processor/

cd build/upload
zip -r ../upload.zip .

cd ../processor
zip -r ../processor.zip .
