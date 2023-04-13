import os
from flask import Flask
from flask_cors import CORS
import boto3
from botocore.exceptions import ClientError


boto_session = boto3.Session(
    aws_access_key_id = 'AKIAVW4WDBYWM3DT23W7',
    aws_secret_access_key = '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',
    region_name='us-east-1'
)
dynamodb = boto_session.resource('dynamodb')
dynamodb_client = boto_session.client('dynamodb')

class FILEINFO:
    def __init__(self, key, location, size):
        self.fileKey = key
        self.fileLocation = location
        self.fileSize = size

class PerformanceMetrics: 
    def __init__(self, CPU, Mem, Disk):
        self.CPU_Usage = CPU
        self.Mem_Usage = Mem
        self.Disk_Usage = Disk

class DB:

    # Create a db and a table
    #    File Info
    def __init__(self):

        ##################### Create a File Info table #########################
        currentTables = dynamodb_client.list_tables()['TableNames']
        tableName = 'fileInfo'
        primaryKey = 'fileKey'
        if 'fileInfo' not in currentTables:
            self.createTable(tableName, primaryKey)
        tableName = 'performanceMetrics'
        primaryKey = 'performanceTimeStamp'
        if 'performanceMetrics' not in currentTables:
            self.createTable(tableName, primaryKey)

    def createTable(self, tableName, primaryKey):
        keySchema = [
            {
                'AttributeName': primaryKey,
                'KeyType': 'HASH'  # Partition key
            }
        ]
        keyAttribute = [
            {
                'AttributeName': primaryKey,
                'AttributeType': 'S'
            }
        ]
        table = dynamodb.create_table(
            TableName = tableName,
            KeySchema = keySchema[:],
            AttributeDefinitions = keyAttribute[:],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            },
            Tags=[
                {
                    'Key': 'TableName',
                    'Value': tableName
                }
            ]
        )
        table.meta.client.get_waiter('table_exists').wait(TableName=tableName)
        return

    #######################################
    ###########    Create    ##############
    ####################################### 
    def insertFileInfo(self, tableName, fileInfo):

        table = dynamodb.Table(tableName)
        table.put_item(
            Item = { 
                'fileKey'     : fileInfo.fileKey,
                'fileSize'    : fileInfo.fileSize,
                'fileLocation': fileInfo.fileLocation
            }
        )
        print("Successfully inserted data into {} table".format(tableName))
        return

    def insertPerformanceMetrics(self, tableName, performanceMetrics):
    
        table = dynamodb.Table(tableName)
        table.put_item(
            Item = { 
                'CPU_Usage' : performanceMetrics.CPU_Usage,
                'Mem_Usage' : performanceMetrics.Mem_Usage,
                'Disk_Usage': performanceMetrics.Disk_Usage
            }
        )
        print("Successfully inserted data into {} table".format(tableName))
        return
    
    #######################################
    ###########     Read     ##############
    #######################################
    def readFileInfo(self, tableName, fileKey):

        table = dynamodb.Table(tableName)
        try:
            response = table.get_item(
                Key={
                    'fileKey': fileKey
                }
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print("Table does not exist")
            elif e.response['Error']['Code'] == 'ValidationError':
                print("Invalid parameter: " + e.response['Error']['Message'])
            else:
                print("Unexpected error: " + e.response['Error']['Message'])
        else:
            if 'Item' not in response:
                print("Item not found :(")
                return None
            else:
                item = response['Item']
                print(item)
                return FILEINFO(**item)


    def readAllFileKeys(self):

        # connection, cursor = self.connect(db='A2_RDBMS')

        # # query
        # tableName = "fileInfo"
        # sql = """
        # SELECT filekey
        # FROM {}
        # """.format(tableName)
        # cursor.execute(sql)
        # records = cursor.fetchall()

        # # disconnect
        # cursor.close()
        # connection.close()

        # # get and return all the keys from db 
        # return [record[0] for record in records]
        return
    
    def readAllFilePaths(self):

        # connection, cursor = self.connect(db='A2_RDBMS')

        # # query
        # tableName = "fileInfo"
        # sql = """
        # SELECT location
        # FROM {}
        # """.format(tableName)
        # cursor.execute(sql)
        # records = cursor.fetchall()

        # # disconnect
        # cursor.close()
        # connection.close()

        # # get and return all the file paths from db 
        # return [record[0] for record in records]
        return

    #######################################
    ###########     Update    #############
    ####################################### 
    def updFileInfo(self, fileInfo):

        # connection, cursor = self.connect(db='A2_RDBMS')
        
        # # Current table is cacheConfigs
        # tableName = "fileInfo"
        # sql = """
        # UPDATE {}
        # SET location = %s, size = %s
        # WHERE fileKey = %s
        # """.format(tableName)
        # val = (fileInfo.location, fileInfo.size, fileInfo.key)
        # cursor.execute(sql, val)

        # # Commit the changes and disconnect
        # connection.commit()
        # cursor.close()
        # connection.close()
        return


    #######################################
    ###########     Delete    #############
    #######################################
    def delFileInfo(self, tableName, fileKey):
        
        table = dynamodb.Table(tableName)
        try:
            response = table.delete_item(
                Key={
                    'fileKey': fileKey
                }
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print("Table does not exist")
            elif e.response['Error']['Code'] == 'ValidationError':
                print("Invalid parameter: " + e.response['Error']['Message'])
            else:
                print("Unexpected error: " + e.response['Error']['Message'])
        else:
            if 'Item' not in response:
                print("Item not found :(")
        return


    def delAllFileInfo(self, tableName):

        table = dynamodb.Table(tableName)
        response = table.scan()
        with table.batch_writer() as batch:
            for item in response['Items']:
                batch.delete_item(
                    Key={
                        'fileKey': item['fileKey']
                    }
                )
        return




webapp = Flask(__name__)
CORS(webapp)
db = DB()
from app import main