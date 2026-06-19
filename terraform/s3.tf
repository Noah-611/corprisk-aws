data "aws_caller_identity" "current" {}

resource "aws_s3_bucket" "reports" {
  bucket = "${var.name_prefix}-${data.aws_caller_identity.current.account_id}-reports"

  tags = {
    Name = "${var.name_prefix}-reports"
  }
}

resource "aws_s3_bucket_public_access_block" "reports" {
  bucket = aws_s3_bucket.reports.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}