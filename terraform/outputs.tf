output "api_url" {
  description = "URL to the API Gateway endpoint"
  value       = aws_apigatewayv2_stage.trut.invoke_url
}
