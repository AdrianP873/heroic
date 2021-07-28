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

    # Call build ECR function and store uri in variable
    repo_uri = build_ecr_repo(app_name, repo_name)

    # Call generate values function
    generate_values_file(values_data, repo_uri, repo_name)

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
    with open("./python_pipeline.yml", "w+") as f_input:
        f_input.write(str(decoded_file_contents))

    with open("./python_pipeline.yml", "r+") as f_output:
        text = f_output.read()
        text = re.sub("NAME_PLACEHOLDER", app, text)
        f_output.seek(0)
        f_output.write(text)
        f_output.truncate()

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
        print('404 Client Error: Ensure your Git personal access token has permissions to manage workflows.')
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

        repo_uri = response['repositories'][0]['repositoryArn']
        
        logger.info("Repository {} already exists. Continuing...".format(app))
        logger.info("Repository URI: {}".format(repo_uri))
        return repo_uri

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

            repo_uri = create_repo['repository']['repositoryArn']

            logger.info("Repository {} created.".format(app))
            logger.info("Repository URI: {}".format(repo_uri))
            return repo_uri

        else:
            print("Something went wrong...")
            print(e.response)
            logger.error("Something went wrong...")

def generate_values_file(data, repo_uri, repo):
    """ Generates a baseline values.yaml manifest to be consumed by the application helm chart """

    # Pull down config file from s3
    logger.info("Pulling down config file python_pipeline.yml")
    s3 = boto3.client("s3")

    s3_data = s3.get_object(
        Bucket="heroic-ap-southeast-2-pipeline-configs",
        Key="python_values.yml"
    )

    logger.info("Decoding values file contents.")
    format_data = s3_data['Body'].read()
    decoded_file_contents = format_data.decode('ascii')

    logger.info("Substituting file content with provided data...")
    os.chdir("/tmp")
    with open("./python_values.yml", "w+") as f_input:
        f_input.write(str(decoded_file_contents))

    with open("./python_values.yml", "r+") as f_output:
        text = f_output.read()
        text_out = re.sub(r"(image_registry)|(cpu_req)|(mem_req)|(cpu_lim)|(mem_lim)|(service_state)|(service_port)|(/default)", lambda match: sub_text(match, data), text)
        f_output.seek(0)
        f_output.write(text_out)
        f_output.truncate()
    
    # Retrieve git secret to access GitHub repo
    ssm = boto3.client("ssm")

    get_secret = ssm.get_parameter(
        Name="GIT_TOKEN",
        WithDecryption=True
    )

    git_url = "https://api.github.com/repos/{owner}/{repo}/contents/python_values.yml".format(owner="adrianp873", repo=repo)
    headers = {"Accept": "application/vnd.github.v3+json", "Authorization": "token " + get_secret["Parameter"]["Value"]}

    # Read values manifest
    values_file = open("./python_values.yml", "r")
    read_file = str(values_file.read())
    values_file.close()

    # Base64 encode manifest file
    file_bytes = read_file.encode('ascii')
    base64_bytes = base64.b64encode(file_bytes)
    base64_file = base64_bytes.decode('ascii')

    data = {"message":"message","content": base64_file}

    # Upload values.yml manifest to GitHub repo
    res = requests.put(git_url, headers=headers, data=json.dumps(data))

    if res.status_code == 404:
        print('404 Client Error: Ensure your Git personal access token has appropriate permissions to upload and commit a file.')
    else:
        print("Pipeline configuration created at {repo}/k8s/python_values.yml".format(repo=repo))




def sub_text(obj_match, data):
    if obj_match.group(1) is not None:
        return "ecr_registry234"
    if obj_match.group(2) is not None:
        return data["requests"]["cpu"]
    if obj_match.group(3) is not None:
        return data["requests"]["memory"]
    if obj_match.group(4) is not None:
        return data["limits"]["cpu"]
    if obj_match.group(5) is not None:
        return data["limits"]["memory"]
    if obj_match.group(6) is not None:
        return data["service"]["enabled"]
    if obj_match.group(7) is not None:
        return data["service"]["port"]
    if obj_match.group(8) is not None:
        return data["service"]["uri"]