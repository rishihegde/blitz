provider "aws" {
  alias  = "s3region"
  region = var.bucket_region
}

resource "aws_s3_bucket" "terrform_state" {
  provider = aws.s3region
  region   = var.bucket_region
  bucket   = var.bucket_name

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "s3versioning" {
  bucket = aws_s3_bucket.terrform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "s3enc" {
  bucket = aws_s3_bucket.terrform_state.bucket

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-up-and-running-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  attribute {
    name = "LockID"
    type = "S"
  }
}
