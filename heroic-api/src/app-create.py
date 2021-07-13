"""
Create an application.
"""

import boto3
from botocore.exceptions import ClientError
import logging
import re, json, requests, os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """ Build baseline pipeline """
    # Parse the app_name and github_url passed to it
    data = json.loads(event['body'])

    app_name = data["app_name"]
    github_url = data["github_url"]
    search_repo = re.search("/(.+?).git", github_url)

    if search_repo:
        repo_name = search_repo.group(1)
        logger.info("Repository name {} found.".format(repo_name))
    else:
        logger.warning("Couldn't find repository name from git URL.")

    logger.info("app_name: {}, github_url: {}, repo_name: {}".format(app_name, github_url, repo_name))

    # Call build pipeline funciton
    build_base_pipeline(app_name, repo_name)

    # Call build ECR function
    build_ecr_repo(app_name, repo_name)

    return_body = {"message": "{} successfully created".format(app_name)}
    return_status = 200

    return {
        'statusCode': return_status,
        'body': json.dumps(return_body)
    }

def build_base_pipeline(app, repo):
    """ Creates a baseline pipeline config and uploads it to Git repo """

    # Pull down config file from s3
    logger.info("Pulling down config file python_pipeline.yml")

    s3 = boto3.client("s3")

    data = s3.get_object(
        Bucket="heroic-ap-southeast-2-pipeline-configs",
        Key="python_pipeline.yml"
    )

    logger.info("Modifying config pipeline file with application name: {}".format(app))

    contents = data['Body'].read()
    
    with open("/tmp/test.txt", "w+") as f:
        f.write(str(contents))

    with open("/tmp/test.txt", "r+") as a:
        text = a.read()
        text = re.sub("NAME_PLACEHOLDER", app, text)
        a.seek(0)
        print(text)

    # Upload the file to the Github Repo
    git_url = "https://api.github.com/repos/{owner}/{repo}/contents/test.txt".format(owner="adrianp873", repo=repo)
    headers = {"Accept": "application/vnd.github.v3+json", "Authorization": "token " + os.environ["GIT_TOKEN"]}
    data = {"message":"message","content":"aGVsbG93b3JsZAo="}

    res = requests.put(git_url, headers=headers, data=json.dumps(data))

def build_ecr_repo(app, repo):
    """ Creates new ECR repo if one doesn't already exist """
    ecr = boto3.client("ecr")

    try:
        response = ecr.describe_repositories(
            repositoryNames=[
                app
            ],
        )
        
        logger.info("Repository {} already exists. Continuing...".format(app))
        return "Repository {} already exists. Continuing...".format(app)

    except ClientError as e:
        if e.response["Error"]["Code"] == "RepositoryNotFoundException":
            #print("Repository {} not found, creating one instead...".format(app))
            logger.info("Repository {} not found, creating one instead...".format(app))

            create_repo = ecr.create_repository(
                repositoryName=app,
                tags=[
                    {
                        "Key": "repo",
                        "Value": repo
                    },
                    {
                        "Key": "env",
                        "Value": "dev"
                    }
                ],
                imageScanningConfiguration={
                    "scanOnPush": True
                },
                encryptionConfiguration={
                    "encryptionType": "KMS"
                }
            )

            logger.info("Repository {} created.".format(app))
            return "Repository {} created.".format(app)

        else:
            print("Something went wrong...")
            print(e.response)
            logger.error("Something went wrong...")