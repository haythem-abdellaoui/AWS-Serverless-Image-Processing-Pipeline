output "upload_bucket_name" {
  value = aws_s3_bucket.uploads.bucket
}

output "upload_bucket_arn" {
  value = aws_s3_bucket.uploads.arn
}

output "processed_bucket_name" {
  value = aws_s3_bucket.processed.bucket
}

output "processed_bucket_arn" {
  value = aws_s3_bucket.processed.arn
}