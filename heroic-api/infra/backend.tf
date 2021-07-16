terraform {
    backend "s3" {
        bucket = "heroic-ap-southeast-2-tf"
        key = "terraform.tfstate"
        region = "ap-southeast-2"
    }
}