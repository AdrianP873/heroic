# lambda function
# Creates application

"""
Create an application.
"""

import boto3

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, context):
    
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