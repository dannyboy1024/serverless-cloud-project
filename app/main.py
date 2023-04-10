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
    requestJson = {
        'key': key_value
    }
    # res = requests.post(webapp_url + '/getFromS3', params=requestJson) # TODO: S3 + DynamoDB
    res = None
    fileInfo = db.readFileInfo('fileInfo', key_value)
    if res.status_code == 400:
        resp = OrderedDict()
        resp["success"] = "false"
        resp["error"] = {
            "code": 400,
            "message": "Target file is not found because the given key is not found."
        }
        response = webapp.response_class(
            response=json.dumps(resp),
            status=400,
            mimetype='application/json'
        )
    else:
        json_response = res.json()
        value = json_response["value"]
        size = json_response["size"]
        content = base64.b64decode(value)
        resp = OrderedDict()
        resp["success"] = "true"
        resp["key"] = key_value
        resp["content"] = bytes.decode(content)
        requestJson = {
            'key': key_value,
            'value': value, 
            'size': size
        }
        # requests.post(memcache_pool_url + '/put', params=requestJson) TODO: AWS Cache service
        response = webapp.response_class(
            response=json.dumps(resp),
            status=200,
            mimetype='application/json'
        )
    return response

@webapp.route('/delete_all', methods=['POST'])
def delete_all():
    """
    Remove all the key and values (files, images) from the database and filesystem
    No inputs required
    """
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