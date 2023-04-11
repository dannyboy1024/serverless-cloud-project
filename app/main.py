from flask import render_template, url_for, request, session, json
from app import webapp, db, FILEINFO
from collections import OrderedDict
import boto3
from pathlib import Path
import os
import hashlib
import base64
import requests
import plotly.graph_objs as go
import pytz
from datetime import datetime, timedelta

# AWS Setup
os_file_path = os.getcwd()
bucket_name = 'ece1779-winter23-a3-bucket'
def provision_aws():
    global s3client
    s3client = boto3.client('s3', region_name='us-east-1')
    print("Provision done")
provision_aws()


@webapp.route('/')
def main():
    return render_template("main.html")

@webapp.route('/upload', methods=['GET', 'POST'])
def upload():
    # upload image with key
    # transfer the bytes into dict
    s3client = boto3.client('s3', region_name='us-east-1')
    data = request.form
    key = data.get('key')
    imageContent = data.get('file')
    value = base64.b64encode(str(imageContent).encode())
    
    imageSize = eval(imageContent).get('size')
    print(eval(imageContent).get('name'))
    filename  = eval(imageContent).get('name')
    requestJson = {
        'key': key,
        'value': value,
        'size': imageSize, 
        'name': filename
    }
    full_file_path = os.path.join(os_file_path, filename)
    # requests.post(memcache_pool_url + '/put', params=requestJson) TODO: AWS Cache service + S3
    # requests.post(webapp_url + '/uploadToDB', params=requestJson) TODO: dynamodb
    if os.path.isfile(full_file_path):
        os.remove(full_file_path)
    with open(full_file_path, 'w') as fp:
        fp.write(value)
    s3client.upload_file(full_file_path, bucket_name, filename)
    db.insertFileInfo(tableName='fileInfo', fileInfo=FILEINFO(key, full_file_path, imageSize))
    
    resp = OrderedDict([("success", "true"), ("key", key)])
    response = webapp.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype='application/json'
    )

    return response

@webapp.route('/retrieve/<key_value>', methods=['GET', 'POST'])
def retrieve(key_value):
    s3client = boto3.client('s3', region_name='us-east-1')
    requestJson = {
        'key': key_value
    }
    # res = requests.post(webapp_url + '/getFromS3', params=requestJson) # TODO: S3 + DynamoDB
    res = None
    # TODO: dynamodb
    fileInfo = db.readFileInfo(key_value)
    if fileInfo != None: 
        filename = fileInfo.location
        fileSize = fileInfo.size
        checkFile = s3client.list_objects_v2(Bucket=bucket_name, Prefix=filename)
        if "Contents" in checkFile:
            full_file_path = os.path.join(os_file_path, filename)
            s3client.download_file(bucket_name, filename, full_file_path)
            value = Path(full_file_path).read_text()
            resp = {
                "success" : "true", 
                "value": value, 
                "size": fileSize
            }
            response = webapp.response_class(
                response=json.dumps(resp),
                status=200,
                mimetype='application/json'
            )
        else:
            response = webapp.response_class(
                response=json.dumps("File Not Found"),
                status=400,
                mimetype='application/json'
            )
    else:
        print("Not found in DB")
        response = webapp.response_class(
            response=json.dumps("Not found in DB"),
            status=400,
            mimetype='application/json'
        )

    return response

@webapp.route('/delete_all', methods=['POST'])
def delete_all():
    """
    Remove all the key and values (files, images) from the database and filesystem
    No inputs required
    """
    s3client = boto3.client('s3', region_name='us-east-1')
    response = s3client.list_objects_v2(Bucket=bucket_name)
    if 'Contents' in response: 
        for obj in response['Contents']:
            s3client.delete_object(Bucket=bucket_name, Key=obj['Key'])
    #db.delAllFileInfo() TODO: dynamodb
    db.delAllFileInfo(tableName='fileInfo')
    
    # requests.post(memcache_pool_url + '/clear') TODO: AWS Cache service
    resp = {
        "success" : "true"
    }
    response = webapp.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype='application/json'
    )
    return response