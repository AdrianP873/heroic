output "heroic_bucket_name" {
    value = aws_s3_bucket.heroic_bucket.id
}

output "heroic_bucket_arn" {
    value = aws_s3_bucket.heroic_bucket.arn
}

output "heroic_bucket_domain_name" {
    value =  aws_s3_bucket.heroic_bucket.heroic_bucket_domain_name
}