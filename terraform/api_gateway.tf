resource "aws_apigatewayv2_api" "trut" {
  name          = "${local.common_tags.Name}-api-gw"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "trut" {
  api_id = aws_apigatewayv2_api.trut.id

  name        = "trut_lambda_stage"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gw.arn

    format = jsonencode({
      requestId               = "$context.requestId"
      sourceIp                = "$context.identity.sourceIp"
      requestTime             = "$context.requestTime"
      protocol                = "$context.protocol"
      httpMethod              = "$context.httpMethod"
      resourcePath            = "$context.resourcePath"
      routeKey                = "$context.routeKey"
      status                  = "$context.status"
      responseLength          = "$context.responseLength"
      integrationErrorMessage = "$context.integrationErrorMessage"
      }
    )
  }
}

resource "aws_apigatewayv2_integration" "trut" {
  api_id = aws_apigatewayv2_api.trut.id

  integration_uri    = aws_lambda_function.trut.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "trut" {
  api_id = aws_apigatewayv2_api.trut.id

  route_key = "POST /calculate"
  target    = "integrations/${aws_apigatewayv2_integration.trut.id}"
}
