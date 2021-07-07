# lambda function
# Creates application

"""
Create an application.
"""

import boto3

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, context):
    """ Build baseline pipeline """
    # Parse the app_name and github_uri passed to it
    app_name = event["app_name"]
    github_url = event["github_url"]

    # Pull down config file from s3
    s3 = boto3.client("s3")

    data = s3.get_object(
        Bucket="heroic-ap-southeast-2-pipeline-configs",
        Key="python_pipeline.yml",
    )
    contents = data['Body'].read()
    print(contents)
    
    with open("/tmp/test.txt", "w+") as f:
        text = f.write(str(data['Body'].read()))

    with open("/tmp/test.txt", "r+") as l:
        text = l.read()
        text = re.sub("NAME_PLACEHOLDER", "THIS_MA_NEW_NAME", text)
        l.seek(0)
        l.truncate()
        print(text)

    # Modify file to put in the app_name and github_uri
    # Upload the file to the Github Repo






# Whatever we pass can be accessed via event["key"]

    #logging.info("meal: {}, ingredients: {}".format(payload["meal"], payload["ingredients"]))
   
    return_status = 200
    return_body = {"message": "{} successfully added.".format("test")}

    return {
        "statusCode": return_status,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST',
            'Content-Type': 'application/json',
        },
        "body": json.dumps(return_body)
    }