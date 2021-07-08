"""
Create an application.
"""

import boto3
import logging
import re, json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """ Build baseline pipeline """
    # Parse the app_name and github_uri passed to it
    app_name = event["app_name"]
    github_url = event["github_url"]

    # Pull down config file from s3
    logging.info("Pulling down config file python_pipeline.yml")

    s3 = boto3.client("s3")

    data = s3.get_object(
        Bucket="heroic-ap-southeast-2-pipeline-configs",
        Key="python_pipeline.yml",
    )

    # Modify file to put in the app_name and github_uri
    logging.info("Modifying config pipeline file with application name: {}".format(app_name)

    contents = data['Body'].read()
    
    with open("/tmp/test.txt", "w+") as f:
        f.write(str(contents))

    with open("/tmp/test.txt", "r+") as a:
        text = a.read()
        text = re.sub("NAME_PLACEHOLDER", app_name, text)
        a.seek(0)
        print(text)

    # Upload the file to the Github Repo

def build_ecr_repo():
    # Check if ECR Repo under app_name exists
    # If repo does not already exist, create one with appropriate repository policy
    pass

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }