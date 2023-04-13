import json
import datetime
import boto3

import urllib.parse
import boto3

print('Loading function')

boto_session = boto3.Session(
    aws_access_key_id = 'AKIAVW4WDBYWM3DT23W7',
    aws_secret_access_key = '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',
    region_name='us-east-1'
)
dynamodb = boto_session.resource('dynamodb')
dynamodb_client = boto_session.client('dynamodb')

s3 = boto3.client('s3')


def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    timestamp = event['timestamp']


    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        print("CONTENT TYPE: " + response['ContentType'])
        return response['ContentType']
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e


