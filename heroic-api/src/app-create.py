"""
Create an application.
"""

import boto3
from botocore.exceptions import ClientError
import logging
import re, json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """ Build baseline pipeline """
    # Parse the app_name and github_url passed to it
    app_name = event["app_name"]
    print(app_name)
    github_url = event["github_url"]

    search_repo = re.search("/(.+?).git", github_url)
    if search_repo:
        repo_name = search_repo.group(1)
        logging.info("Repository name {} found.".format(repo_name))
    else:
        logging.warning("Couldn't find repository name from git URL.")

    # Pull down config file from s3
    logging.info("Pulling down config file python_pipeline.yml")

    s3 = boto3.client("s3")

    data = s3.get_object(
        Bucket="heroic-ap-southeast-2-pipeline-configs",
        Key="python_pipeline.yml"
    )

    # Modify file to put in the app_name and github_uri
    logging.info("Modifying config pipeline file with application name: {}".format(app_name))

    contents = data['Body'].read()
    
    with open("/tmp/test.txt", "w+") as f:
        f.write(str(contents))

    with open("/tmp/test.txt", "r+") as a:
        text = a.read()
        text = re.sub("NAME_PLACEHOLDER", app_name, text)
        a.seek(0)
        print(text)

    # Upload the file to the Github Repo
    ecr = boto3.client("ecr")

    try:
        response = ecr.describe_repositories(
            repositoryNames=[
                app_name
            ],
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "RepositoryNotFoundException":
            print("Repository {} not found, creating one instead...".format(app_name))
            logging.info("Repository {} not found, creating one instead...".format(app_name))

            create_repo = ecr.create_repository(
                repositoryName=app_name,
                tags=[
                    {
                        "repo": repo_name,
                        "env": dev
                    }
                ],
                imageScanningConfiguration={
                    "scanOnPush": True
                },
                encryptionConfiguration={
                    encryptionType: "KMS"
                }
            )
        else:
            print("Something went wrong...")
            print(e.response)
            logging.error("Something went wrong...")

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

def build_ecr_repo():
    """ Creates new ECR repo if one doesn't already exist """
    # Check if ECR Repo under app_name exists. If not, create new one
    # Need to pass app_name to this function 
    pass

