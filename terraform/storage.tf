resource "aws_s3_bucket" "lambda" {
  bucket = var.lambda_bucket
}

resource "aws_s3_object" "lambda_zip" {
  bucket = aws_s3_bucket.lambda.id
  key    = "trut.zip"
  source = var.lambda_archive
}
