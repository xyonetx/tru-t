terraform {
  required_version = ">= 1.2.6, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.24.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.2.0"
    }
  }
  backend "s3" {
    bucket               = "xyonetx-terraform"
    key                  = "terraform-trut-lambda.state"
    region               = "us-east-2"
    workspace_key_prefix = "workspace"
  }
}

locals {
  stack = lower(terraform.workspace)
  common_tags = {
    Name      = "${local.stack}-trut"
    Terraform = "True"
  }
}

provider "aws" {
  region = "us-east-2"
  default_tags {
    tags = local.common_tags
  }
}


