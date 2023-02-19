import os
import json
import uuid
import boto3
import time
from dynamodb_json import json_util as json_db

# getLogs
def lambda_handler(event, context):
    print('received event:')
    print(event)

    # Static Variables
    db_client = boto3.client('dynamodb')
    DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']

    body = json.loads(event['body'])

    startTime = 0
    if 'startTime' in body:
        startTime = body['startTime']
    
    endTime = time.time()
    if 'endTime' in body:
        endTime = body['endTime']

    # Get log objects
    response = db_client.scan(
      TableName=DYNAMODB_TABLE,
      FilterExpression='timeCreated BETWEEN :startTime AND :endTime',
      ExpressionAttributeValues= {
          ':startTime' : {'N': str(startTime)},
          ':endTime' : {'N': str(endTime)},
      }
    )

    body = {"logs": json_db.loads(response['Items'])}

    return {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        "body": json.dumps(body),
    }

