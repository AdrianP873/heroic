#!/bin/sh
set -x

STATE_BUCKET="heroic-${REGION}-tf"

terraform init \
  -backend-config="bucket=${STATE_BUCKET}"
  -backend-config="region=${REGION}"

terraform workspace select ${ENV} || terraform workspace new ${ENV}

terraform apply -auto-approve