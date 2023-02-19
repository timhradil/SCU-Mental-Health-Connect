import os
import json
import uuid
import boto3
import time

# putLog
def lambda_handler(event, context):
    print('received event:')
    print(event)

    # Static Variables
    db_client = boto3.client('dynamodb')
    DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']

    body = json.loads(event['body'])

    # Create item object
    logId = str(uuid.uuid4())
    timeCreated = time.time()
    if 'timeCreated' in body:
        timeCreated = body['timeCreated']
    item = {
        'logId': {'S': logId},
        'phone': {'S': body['phoneNumber']},
        'outcome': {'S': body['outcome']},
        'timeCreated': {'N': str(timeCreated)},
    }

    response = db_client.put_item(
      TableName=DYNAMODB_TABLE,
      Item=item,
    )

    return {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        "body": json.dumps({}),
    }

