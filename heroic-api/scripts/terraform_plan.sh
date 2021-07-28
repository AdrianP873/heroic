#!/bin/sh
set -x

STATE_BUCKET="heroic-${REGION}-tf"

cd heroic-api/infra

terraform init \
  -backend-config="bucket=${STATE_BUCKET}"
  -backend-config="region=${REGION}"

terraform workspace list
terraform workspace select ${ENV} || terraform workspace new ${ENV}

terraform plan \
  -var "env=${ENV}" \
  -var "region=${REGION}" \
  -var "vpc_id"=${VPC_ID}

terraform show