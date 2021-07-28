variable "vpc_id" {
    type = string
    description = "Default vpc ID."
}

variable "env" {
    type        = string
    description = "The environment e.g. dev, stg, prd."
}

variable "region" {
    type        = string
    description = "Region to deploy resources into."
    default     = "ap-southeast-2"
}