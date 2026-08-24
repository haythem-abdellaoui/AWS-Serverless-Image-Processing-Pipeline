output "api_id" {
  value = aws_api_gateway_rest_api.this.id
}

output "upload_url" {
  value = "${aws_api_gateway_stage.dev.invoke_url}/upload"
}