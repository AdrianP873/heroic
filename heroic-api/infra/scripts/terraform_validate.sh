#!/bin/sh
cd infra
terraform init -backend=false
terraform validate