resource "aws_cloudwatch_log_group" "trut" {
  name              = "/aws/lambda/${aws_lambda_function.trut.function_name}"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "api_gw" {
  name              = "/aws/api_gw/${aws_apigatewayv2_api.trut.name}"
  retention_in_days = 30
}
