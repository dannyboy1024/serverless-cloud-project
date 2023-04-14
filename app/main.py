from flask import render_template, url_for, request, session, json
from app import webapp, db, FILEINFO
from collections import OrderedDict
import boto3
from pathlib import Path
import os
# import hashlib
import base64
import requests
# import plotly.graph_objs as go
# import pytz
from datetime import datetime, timedelta

# AWS Setup
webapp_url = 'https://3bynfupmn3.execute-api.us-east-1.amazonaws.com/dev'
webapp_url = 'http://127.0.0.1:5000'
os_file_path = os.getcwd()
bucket_name = 'ece1779-a3-files'
def provision_aws():
    global s3client
    s3client = boto3.client('s3', region_name='us-east-1')
    print("Provision done")
provision_aws()


@webapp.route('/')
def main():
    return render_template("main.html")

#################
# Helper routes #
#################
@webapp.route('/helper/uploadToDBandS3', methods=['GET', 'POST'])
def uploadToDBandS3():
    """
    Upload the key to the database
    Store the value as a file in the local file system, key as filename
    key: string
    value: string (For images, base64 encoded string)
    """
    key = request.args.get('key')
    value = request.args.get('value')
    size = request.args.get('size')
    filename  = request.args.get('name')

    full_file_path = os.path.join(os_file_path, filename)
    if os.path.isfile(full_file_path):
        os.remove(full_file_path)
    with open(full_file_path, 'w') as fp:
        fp.write(value)
    s3client.upload_file(full_file_path, bucket_name, filename)
    db.insertFileInfo(tableName='fileInfo', fileInfo=FILEINFO(key, full_file_path, size))

    resp = {
        "success" : "true"
    }
    response = webapp.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype='application/json'
    )
    return response

@webapp.route('/helper/getFromS3', methods=['GET', 'POST'])
def getFromS3():
    """
    Fetch the value (file, or image) from the file system given a key
    key: string
    """
    key = str(request.args.get('key'))
    fileInfo = db.readFileInfo(tableName='fileInfo', fileKey=key)
    if fileInfo != None: 
        filename = fileInfo.fileLocation.split('\\')[-1]
        fileSize = fileInfo.fileSize
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


#################
# Routes        #
#################
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
    # requests.post(memcache_pool_url + '/put', params=requestJson) TODO: AWS Cache service
    requests.post(webapp_url+'/helper/uploadToDBandS3', params=requestJson)
    
    resp = OrderedDict([("success", "true"), ("key", key)])
    response = webapp.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype='application/json'
    )

    return response

@webapp.route('/retrieve', methods=['GET', 'POST'])
def retrieve():

    # get, upload image with key
    # retrieve image
    data = request.form
    key_value = str(data.get('key'))
    requestJson = {
        'key': key_value
    }
    res = requests.post(webapp_url+'/helper/getFromS3', params=requestJson)
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
        response = webapp.response_class(
            response=json.dumps(resp),
            status=200,
            mimetype='application/json'
        )
    return response

@webapp.route('/delete_all', methods=['GET', 'POST'])
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