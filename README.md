# heroic

## Requirements:
- Your GitHub repo requires AWS credentials (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY) configured as <a href="https://docs.github.com/en/actions/reference/encrypted-secrets">GitHub Actions secrets</a>. This allows the provisioned pipeline to push docker images to AWS ECR.
- You have a GitHub Personal Access Token stored in Systems Manager Parameter Store under the key "GIT_TOKEN".

## To do
- Provision a bucket with Terraform to hold pipeline config files. Grant access to lambda function role.
- In app-create.py, think of a way to dynamically add the environment (and maybe owner) to ECR repository tags to keep consistency.
- Create lambda layer for requests library - Now being packed with SAM
- Fix IAM permissions in template.yaml (least privilege)
- Create an automated way to manage secrets (that aren't revealed in the TF state file)
- Run SAM validate on template file in CI

## Design Decisions
- Monorepo vs Polyrepo
- AWS SAM vs Terraform for Serverless
- Heroic-charts location i.e. separate hosted repo vs deploy directly from heroic repo
https://docs.github.com/en/actions/guides/building-and-testing-python#testing-your-code
