import json
import datetime
import boto3

print('Loading function')

boto_session = boto3.Session(
    aws_access_key_id = 'AKIAVW4WDBYWM3DT23W7',
    aws_secret_access_key = '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',
    region_name='us-east-1'
)
dynamodb = boto_session.resource('dynamodb')
dynamodb_client = boto_session.client('dynamodb')



def lambda_handler(event, context): 
    timestamp = event['timestamp']
    CPU_Usage = event['Metrics']['CPU_Usage']
    Mem_Usage = event['Metrics']['Mem_Usage']
    Disk_Usage = event['Metrics']['Disk_Usage']

    try:
        tableName = 'performanceMetrics'
        table = dynamodb.Table(tableName)
        table.put_item(
            Item = { 
                'performanceTimeStamp'  : timestamp, 
                'CPU_Usage'             : CPU_Usage,
                'Mem_Usage'             : Mem_Usage,
                'Disk_Usage'            : Disk_Usage
            }
        )
        #print("CONTENT TYPE: " + response['ContentType'])
        #return response['ContentType']
        response = {
            'statusCode': 200,
            'body': json.dumps("OK")
        }

        return response
    except Exception as e:
        print("Error:", e)
        return "Error:" + e


