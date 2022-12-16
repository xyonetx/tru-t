variable "lambda_bucket" {
  description = "The name of the bucket where the lambda archive will be uploaded to"
  type        = string
}

variable "lambda_archive" {
  description = "The zip file for use in Lambda. Assumed to be one folder up."
  type        = string
}
