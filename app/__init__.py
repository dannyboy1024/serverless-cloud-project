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
s3client = boto_session.client('s3')
rekclient = boto_session.client('rekognition')
dynamodb = boto_session.resource('dynamodb')
dynamodb_client = boto_session.client('dynamodb')

class ACCOUNTINFO:
    def __init__(self, accoID, accoPasswd):
        self.accoID     = accoID
        self.accoPasswd = accoPasswd

class ALBUMINFO:
    def __init__(self, albumName, albumType):
        self.albumName = albumName
        self.albumType = albumType

class FILEINFO:
    def __init__(self, fileName, fileBucket, fileLocation, fileSize):
        self.fileName     = fileName
        self.fileBucket   = fileBucket
        self.fileLocation = fileLocation
        self.fileSize     = fileSize

class PerformanceMetrics: 
    def __init__(self, performanceTimeStamp, CPU, Mem, Disk):
        self.performanceTimeStamp = performanceTimeStamp
        self.CPU_Usage = CPU
        self.Mem_Usage = Mem
        self.Disk_Usage = Disk

class DB:

    def __init__(self):

        # List all the tables
        currentTables = dynamodb_client.list_tables()['TableNames']

        # Initialize an account table
        tableName = 'accounts'
        primaryKey = 'accoID'
        if 'accounts' not in currentTables:
            self.createTable(tableName, primaryKey)

        # Initialize a performance metric table
        tableName = 'performanceMetrics'
        primaryKey = 'performanceTimeStamp'
        if 'performanceMetrics' not in currentTables:
            self.createTable(tableName, primaryKey)
        
        # Table name -> pKey, sKey names
        self.TABLE_KEY_MP = {
            'accounts'           : {'pKey' : 'accoID',               'sKey' : None        },
            'album'              : {'pKey' : 'albumName',            'sKey' : 'albumType' },
            'image'              : {'pKey' : 'fileName',             'sKey' : None        },
            'performanceMetrics' : {'pKey' : 'performanceTimeStamp', 'sKey' : None        }
        }

    #######################################
    ###########    Create    ##############
    ####################################### 
    def createTable(self, tableName, pKeyName, sKeyName=None):
        if sKeyName == None:
            # Simple
            keySchema = [
                {
                    'AttributeName': pKeyName,
                    'KeyType': 'HASH'  # Partition key
                }
            ]
            keyAttribute = [
                {
                    'AttributeName': pKeyName,
                    'AttributeType': 'S'
                }
            ]
        else:
            # Composite
            keySchema = [
                {
                    'AttributeName': pKeyName,
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': sKeyName,
                    'KeyType': 'RANGE'  # Sort key
                }
            ]
            keyAttribute = [
                {
                    'AttributeName': pKeyName,
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': sKeyName,
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

    def insertEntry(self, tableName, entryInfo):
        table = dynamodb.Table(tableName)
        if tableName == 'accounts':
            table.put_item(
                Item = { 
                    'accoID'     : entryInfo.accoID,
                    'accoPasswd' : entryInfo.accoPasswd,
                }
            )
        elif 'album' in tableName:
            table.put_item(
                Item = {
                    'albumName'  : entryInfo.albumName,
                    'albumType'  : entryInfo.albumType
                }
            )
        elif 'image' in tableName:
            table.put_item(
                Item = { 
                    'fileName'    : entryInfo.fileName,
                    'fileBucket'  : entryInfo.fileBucket,
                    'fileLocation': entryInfo.fileLocation,
                    'fileSize'    : entryInfo.fileSize
                }
            )
        print("Successfully inserted data into {} table".format(tableName))
        return

    def insertPerformanceMetrics(self, tableName, performanceMetrics):
    
        table = dynamodb.Table(tableName)
        table.put_item(
            Item = { 
                'performanceTimeStamp'  : performanceMetrics.performanceTimeStamp, 
                'CPU_Usage'             : performanceMetrics.CPU_Usage,
                'Mem_Usage'             : performanceMetrics.Mem_Usage,
                'Disk_Usage'            : performanceMetrics.Disk_Usage
            }
        )
        print("Successfully inserted data into {} table".format(tableName))
        return

    #######################################
    ###########     Read     ##############
    #######################################
    def readEntry(self, tableName, pKey, sKey=None):

        table   = dynamodb.Table(tableName)
        tableType = 'accounts'
        if 'image' in tableName:
            tableType = 'image'
        elif 'album' in tableName:
            tableType = 'album'
        pKeyName = self.TABLE_KEY_MP[tableType]['pKey']
        sKeyName = self.TABLE_KEY_MP[tableType]['sKey']
        try:
            req = {pKeyName : pKey} if sKey==None else {pKeyName : pKey, sKeyName : sKey}
            response = table.get_item(
                Key = req
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
                if tableName == 'accounts':
                    return ACCOUNTINFO(**item)
                elif 'album' in tableName:
                    return ALBUMINFO(**item)
                elif 'images' in tableName:
                    return FILEINFO(**item)

    def readEntries(self, tableName, attriName, attriVal):
        table = dynamodb.Table(tableName)
        response = table.scan()
        entries = []
        for item in response['Items']:
            if item[attriName] == attriVal:
                if tableName == 'accounts':
                    entries.append(ACCOUNTINFO(**item))
                elif 'album' in tableName:
                    entries.append(ALBUMINFO(**item))
                elif 'image' in tableName: 
                    entries.append(FILEINFO(**item))
        return entries

    def readAllEntries(self, tableName):
        currentTables = dynamodb_client.list_tables()['TableNames']
        if tableName not in currentTables:
            return []
        table = dynamodb.Table(tableName)
        response = table.scan()
        if tableName == 'accounts':
            return [ACCOUNTINFO(**item) for item in response['Items']]
        elif 'album' in tableName:
            return [ALBUMINFO(**item) for item in response['Items']]
        elif 'image' in tableName:
            return [FILEINFO(**item) for item in response['Items']]


    #######################################
    ###########     Delete    #############
    #######################################
    def deleteEntry(self, tableName, pKey, sKey=None):

        table   = dynamodb.Table(tableName)
        tableType = 'accounts'
        if 'image' in tableName:
            tableType = 'image'
        elif 'album' in tableName:
            tableType = 'album'
        pKeyName = self.TABLE_KEY_MP[tableType]['pKey']
        sKeyName = self.TABLE_KEY_MP[tableType]['sKey']
        try:
            req = {pKeyName : pKey} if sKey==None else {pKeyName : pKey, sKeyName : sKey}
            response = table.delete_item(
                Key = req
            )
            table.meta.client.get_waiter('table_exists').wait(TableName=tableName)
        except ClientError as e:
            print("Problem request is: ", req)
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print("Table does not exist")
            elif e.response['Error']['Code'] == 'ValidationError':
                print("Invalid parameter: " + e.response['Error']['Message'])
            else:
                print("Unexpected error: " + e.response['Error']['Message'])
            return None
        
        return True

    def deleteEntries(self, tableName, attriName, attriVal):
        table = dynamodb.Table(tableName)
        tableType = 'accounts'
        if 'image' in tableName:
            tableType = 'image'
        elif 'album' in tableName:
            tableType = 'album'
        pKeyName = self.TABLE_KEY_MP[tableType]['pKey']
        sKeyName = self.TABLE_KEY_MP[tableType]['sKey']

        response = table.scan()
        for item in response['Items']:
            print('item', item)
            if item[attriName] == attriVal:
                if tableType == 'album':
                    print('pKeyName = ' + pKeyName, 'sKeyName = ' + sKeyName)
                    self.deleteEntry(tableName, item[pKeyName], item[sKeyName])
                else:
                    self.deleteEntry(tableName, item[pKeyName])

    def deleteTable(self, tableName):
        # dynamodb_client.delete_table(TableName=tableName)
        table = dynamodb.Table(tableName)
        table.delete()
        table.wait_until_not_exists()

    




webapp = Flask(__name__)
webapp.secret_key = 'your_secret_key_here'
CORS(webapp)
db = DB()
from app import main