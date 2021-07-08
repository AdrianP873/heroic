# heroic

## Requirements:
- Your GitHub repo requires AWS credentials (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY) configured as <a href="https://docs.github.com/en/actions/reference/encrypted-secrets">GitHub Actions secrets</a>. This allows the provisioned pipeline to push docker images to AWS ECR.

## To do
- Provision a bucket with Terraform to hold pipeline config files. Grant access to lambda function role.
- In app-create.py, think of a way to dynamically add the environment (and maybe owner) to ECR repository tags to keep consistency.
