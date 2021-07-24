# heroic

## Requirements:
- Your GitHub repo requires AWS credentials (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY) configured as <a href="https://docs.github.com/en/actions/reference/encrypted-secrets">GitHub Actions secrets</a>. This allows the provisioned pipeline to push docker images to AWS ECR.
- You have a GitHub Personal Access Token stored in Systems Manager Parameter Store under the key "GIT_TOKEN". This token requires full repo and workflow permissions.

## To do
- Provision a bucket with Terraform to hold pipeline config files. Grant access to lambda function role.
- In app-create.py, think of a way to dynamically add the environment (and maybe owner) to ECR repository tags to keep consistency.
- Create lambda layer for requests library - Now being packed with SAM
- Fix IAM permissions in template.yaml (least privilege)
- Create an automated way to manage secrets (that aren't revealed in the TF state file)
- Run SAM validate on template file in CI
- Add test after changes to src code i.e. invoke API-GW
- If modify heroic-api/templates/python_pipe.yml, have CI lint/validate the yaml and upload it to s3 bucket
- Template, package, test and deploy application chart
- Created heroic-api bucket manually, need to TF this. Not sure where heroic-api-sam bucket is being created, but needs to be deleted and use heroic-api with prefix instead.
- Fix bug where App returns 'app created successfully" even when it isn't e.g. when passing in a Git Repo that doesn't exist or is not authorized to access.

## Design Decisions
- Monorepo vs Polyrepo
- AWS SAM vs Terraform for Serverless
- Heroic-charts location i.e. separate hosted repo vs deploy directly from heroic repo
https://docs.github.com/en/actions/guides/building-and-testing-python#testing-your-code
- Kubernetes offering: Kops vs kubeadm - for personal project with no traffic its ok because cheap and within free tier if I shut down when not using. To actually use this tool, use EKS.

## Next Steps:
- Helm scripts work but fail because no k8s cluster is reachable. Need to stand up either a kops cluster on AWS free tier, or NAT my home router and run it locally with minikube.

## Workflows
### application-chart-workflow.yaml
- Lints, templates, tests and packages helm chart, then publishes it to s3. This chart is used to deploy an application to a K8s cluster.

### pipeline.yml
- Provisions base infrastructure with Terraform
- Deploys serverless application with SAM (provions API-GW + Lambda)

## FAQ
Q. Heroic is returning a 404 error.
A. Ensure that your repository exists and your Git personal access token has permissions to manage workflows and commit a file.