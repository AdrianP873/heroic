locals {
    common_tags = {
        env   = var.env
        owner = "AdrianP873"
        repo  = "heroic"
    }
}

data "aws_iam_role" "lambda-execution-role" {
  name = "heroic-lambda-execution-role-${var.env}"
}

resource "aws_s3_bucket" "heroic_bucket" {
  bucket = "heroic-ap-southeast-2-pipeline-configs"
  acl    = "private"
  policy = <<POLICY
{
  "Id": "LambdaS3BucketPolicy",
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "LambdaS3BucketPolicy",
      "Action": [
        "s3:GetObject"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:s3:::heroic-ap-southeast-2-pipeline-configs/*"
      ],
      "Principal": {
        "AWS": [
          "${data.aws_iam_role.lambda-execution-role.arn}"
        ]
      }
    }
  ]
}
POLICY

  tags = local.common_tags
}