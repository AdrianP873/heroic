"""
Create an application.
"""

import boto3
from botocore.exceptions import ClientError
import logging
import re, json, requests, base64, os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """ Build baseline pipeline """
    # Parse the app_name and github_url passed to it
    data = json.loads(event["body"])
    values_data = data["data"]

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

    # Call generate values function
    generate_values_file(values_data)

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

    logger.info("Decoding config file contents.")
    format_data = data['Body'].read()
    decoded_file_contents = format_data.decode('ascii')

    logger.info("Modifying config pipeline file with application name: {}".format(app))

    os.chdir("/tmp")
    with open("./python_pipeline.yml", "w+") as f:
        f.write(str(decoded_file_contents))

    with open("./python_pipeline.yml", "r+") as a:
        text = a.read()
        text = re.sub("NAME_PLACEHOLDER", app, text)
        a.seek(0)

    # Retrieve git secret and upload file to the Github Repo
    ssm = boto3.client("ssm")

    get_secret = ssm.get_parameter(
        Name="GIT_TOKEN",
        WithDecryption=True
    )

    git_url = "https://api.github.com/repos/{owner}/{repo}/contents/.github/workflows/python_pipeline.yml".format(owner="adrianp873", repo=repo)
    headers = {"Accept": "application/vnd.github.v3+json", "Authorization": "token " + get_secret["Parameter"]["Value"]}

    # Read pipeline config file
    pipeline_file = open("python_pipeline.yml", "r")
    read_file = str(pipeline_file.read())
    pipeline_file.close()

    # Base64 encode pipeline file
    file_bytes = read_file.encode('ascii')
    base64_bytes = base64.b64encode(file_bytes)
    base64_file = base64_bytes.decode('ascii')

    data = {"message":"message","content": base64_file}

    res = requests.put(git_url, headers=headers, data=json.dumps(data))

    if res.status_code == 404:
        # This may occur if the .github/workflows directory already exists.)
        print('404 Client Error: the .github/workflows directory likely already exists. See limitations in README.')
    else:
        print("Pipeline configuration created at {repo}/.github/workflows/python_pipeline.yml".format(repo=repo))

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

def generate_values_file(data):
    print(data)