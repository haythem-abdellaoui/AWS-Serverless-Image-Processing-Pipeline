resource "aws_s3_bucket" "uploads" {
  bucket = var.upload_bucket_name
}

resource "aws_s3_bucket" "processed" {
  bucket = var.processed_bucket_name
}

