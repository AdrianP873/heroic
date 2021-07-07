#!/bin/sh
set -x

STATE_BUCKET="heroic-${REGION}-tf"

terraform init \
  -backend-config="bucket=${STATE_BUCKET}"