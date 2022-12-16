resource "aws_lambda_function" "trut" {
  function_name = "${local.common_tags.Name}-calculator"
  architectures = ["x86_64"]
  s3_bucket     = aws_s3_bucket.lambda.id
  s3_key        = aws_s3_object.lambda_zip.key
  package_type  = "Zip"
  runtime       = "python3.9"
  handler       = "aws_lambda_handler.lambda_entrypoint"
  memory_size   = 1024
  role          = aws_iam_role.lambda_exec.arn
}

resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.trut.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.trut.execution_arn}/*/*"
}
