#!/bin/sh
cd heroic-api/infra
terraform init -backend=false
terraform validate