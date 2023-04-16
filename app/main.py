from flask import render_template, url_for, request, session, json
from app import webapp, db, FILEINFO, ALBUMINFO, ACCOUNTINFO
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
# webapp_url = 'https://3bynfupmn3.execute-api.us-east-1.amazonaws.com/dev'
# os_file_path = '/tmpDir'
webapp_url = 'http://127.0.0.1:5000'
os_file_path = os.getcwd()
bucket_name = 'ece1779-a3-files'
def provision_aws():
    global s3client, rekclient
    s3client  = boto3.client('s3', region_name='us-east-1')
    rekclient = boto3.client('rekognition', region_name='us-east-1')
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
        filename = fileInfo.fileLocation.split('/')[-1]
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
# Tmp routes    #
#################
@webapp.route('/retrieve', methods=['GET', 'POST'])
def retrieve():

    # get, upload image with key
    # retrieve image
    data = request.form
    key = str(data.get('key'))
    # requestJson = {
    #     'key': key
    # }
    # res = requests.post(webapp_url+'/helper/getFromS3', params=requestJson)
    fileInfo = db.readFileInfo(tableName='fileInfo', fileKey=key)
    if fileInfo != None: 
        # filename = fileInfo.fileLocation.split('/')[-1]
        filename = fileInfo.fileLocation.split('\\')[-1]
        checkFile = s3client.list_objects_v2(Bucket=bucket_name, Prefix=filename)
        full_file_path = os.path.join(os_file_path, filename)
        s3client.download_file(bucket_name, filename, full_file_path)
        value = bytes.decode(base64.b64decode(Path(full_file_path).read_text()))
        resp = OrderedDict()
        resp["success"] = "true"
        resp["key"] = key
        resp["content"] = value
        response = webapp.response_class(
            response=json.dumps(resp),
            status=200,
            mimetype='application/json'
        )
        return response


#################
# Routes        #
#################
@webapp.route('/upload_image', methods=['GET', 'POST'])
def upload_image():

    """
    Upload an image to an album
    Inputs:
        - Album name [String]
        - Image content [Bytes?]
    Outputs:
        - Success message [String]
        - Album name [String]
    """

    # Get album name and image
    data          = request.form
    albumName     = str(data.get('album'))
    imageContent  = data.get('image')
    imageName     = str(eval(imageContent).get('name'))
    imageSize     = str(eval(imageContent).get('size'))
    imageLocation = os.path.join(os_file_path, imageName)
    value         = base64.b64encode(str(imageContent).encode())
    if os.path.isfile(imageLocation):
        os.remove(imageLocation)
    with open(imageLocation, 'w') as fp:
        fp.write(value)
    isAuto = session['isAuto']
    mode   = 'auto' if isAuto else 'manual'
    
    # Lookup the image. Delete it if it exists.
    accoID = session['currentUser']
    imageTableName = accoID+'/'+albumName+'/'+mode+'/images'
    imageBucketName = imageTableName
    imageInfo = db.readEntry(imageTableName, imageName)
    if imageInfo != None:
        s3client.delete_object(Bucket=imageTableName, Prefix=imageName)
        db.deleteEntry(imageTableName, imageName)
    
    # Upload the image to the s3 bucket and insert a new entry to the image table
    s3client.upload_file(imageLocation, imageTableName, imageName)
    db.insertEntry(imageTableName, FILEINFO(imageName, imageBucketName, imageLocation, imageSize))
    
    resp = OrderedDict([("success", True), ("album", albumName)])
    response = webapp.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype='application/json'
    )

    return response

@webapp.route('/display_image', methods=['GET', 'POST'])
def display_image():
    
    """
    Display an image in an album
    Inputs:
        - Album name [String]
        - Image name [String]
    Outputs:
        - Success / Fail [Boolean]
        - Image content [?]
    """

    # Get album and image name
    data = request.form
    albumName = str(data.get('album'))
    imageName = str(data.get('name'))
    isAuto = session['isAuto']
    mode = 'auto' if isAuto else 'manual'

    # Check if the image exists
    accoID = session['currentUser']
    imageTableName = accoID+'/'+albumName+'/'+mode+'/images'
    imageInfo = db.readEntry(imageTableName, imageName)
    bucketName = imageInfo.fileBucket

    # Get the image object from the s3 bucket
    full_file_path = os.path.join(os_file_path, imageName)
    s3client.download_file(bucketName, imageName, full_file_path)
    value = bytes.decode(base64.b64decode(Path(full_file_path).read_text()))
    resp = {
        "success" : True,
        "image" : value
    }
    response = webapp.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype='application/json'
    )
    return response

@webapp.route('/delete_image', methods=['GET', 'POST'])
def delete_image():

    """
    Delete an image from an album
    Inputs:
        - Album name [String]
        - Image name [String]
    Outputs:
        - Success / Fail [Boolean]
    """

    # Get album name
    data      = request.form
    albumName = str(data.get('album'))
    imageName = str(data.get('name'))
    isAuto    = session['isAuto']
    mode      = 'auto' if isAuto else 'manual'

    # Delete the image entry from the image table
    accoID = session['currentUser']
    imageTableName = accoID+'/'+albumName+'/'+mode+'/images'
    imageInfo = db.readEntry(imageTableName, imageName)
    bucketName = imageInfo.fileBucket
    if (isAuto):
        res = db.deleteEntry(bucketName, imageName)
    res = db.deleteEntry(imageTableName, imageName)
    if res == None:
        # Not found in DB
        resp = {
            'success' : False,
            'message' : 'Image not found :('
        }
        response = webapp.response_class(
            response=json.dumps(resp),
            status=400,
            mimetype='application/json'
        )
        return response

    # Delete the image from the s3 bucket
    s3client.delete_object(Bucket=bucketName, Prefix=imageName)
    resp = {
        'success' : True,
        'message' : 'Image found :)'
    }
    response = webapp.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype='application/json'
    )
    return response
    

@webapp.route('/create_album', methods=['GET', 'POST'])
def create_manual_album():
    """
    Create an empty album
    Inputs:
        - Album name [String]
    Outputs:
        - Success / Fail [Boolean]
    """

    # Get album name
    data = request.form
    albumName = str(data.get('album'))
    mode = 'manual'

    # Lookup the album table of the user
    accoID = session['currentUser']
    albumTableName = accoID+'/albums'
    album = db.readEntry(albumTableName, albumName, mode)
    if album != None:
        # Album already exists
        resp = {
            "success" : False,
            "message" : 'Album already exists :('
        }
        response = webapp.response_class(
            response=json.dumps(resp),
            status=400,
            mimetype='application/json'
        )
        return response

    # Insert the new album
    db.insertEntry(albumTableName, ALBUMINFO(albumName, 'manual'))

    # Create a new table of images
    imageTableName = accoID+'/'+album.albumName+'/'+mode+'/images'
    pKeyName = 'fileName'
    db.createTable(imageTableName, pKeyName)

    # Create an s3 bucket for the new album
    s3client.create_bucket(Bucket=imageTableName)

    resp = {
        "success" : True,
        "message" : "New album created :)"
    }
    response = webapp.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype='application/json'
    )
    return response

@webapp.route('/sage_create_albums', methods=['GET', 'POST'])
def sage_create_albums():
    
    """
    Automatically categorize images using labels 
    Inputs:
        - Enable / Disable sage mode [boolean]
    Outputs:
        - Success message [String]
        - Album names [List]
    """

    # Get the mode we are entering
    data = request.form
    isAuto = str(data.get('isAuto'))
    accoID = session['currentUser']
    session['isAuto'] = isAuto
    mode = 'auto' if isAuto else 'manual'
    covers = []

    # Entering the auto mode
    #     1. Delete all the existing auto album entries and their image tables 
    #     2. List all images from all file buckets
    #     3. Create a label map through image labels using rekognition
    #     4. Create albums using the label map
    #     5. Insert new auto album entries and create new image tables
    #     6. Return the automatically created album names and their covers
    if isAuto:

        # Delete all the existing auto album entries and their image tables 
        albumTableName = accoID+'/albums'
        albumInfoList = db.readEntries(albumTableName, attriName='albumType', attriVal='auto')
        for albumInfo in albumInfoList:
            albumName = albumInfo.albumName
            imageTableName = accoID+'/'+albumName+'/'+mode+'/images'
            db.deleteTable(imageTableName)
        db.deleteEntries(albumTableName, attriName='albumType', attriVal='auto')

        # List all images from all file buckets
        allImageReqs = []
        albumInfoList = db.readAllEntries(albumTableName)
        for albumInfo in albumInfoList:
            albumName = albumInfo.albumName
            imageTableName = accoID+'/'+albumName+'/'+mode+'/images'
            imageInfoList = db.readAllEntries(imageTableName)
            for imageInfo in imageInfoList:
                req = {'S3Object': {'Bucket': imageTableName, 'Name': imageInfo.fileName}}
                allImageReqs.append(req)

        # Create a label map through image labels using rekognition
        labelMp = {}
        for idx in range(len(allImageReqs)):
            # detect labels in the image
            resp = rekclient.detect_labels(Image=allImageReqs[idx])
            for label in resp['Labels']:
                labelName = label['Name']
                if labelName in labelMp:
                    labelMp[labelName].append(idx)
                else:
                    labelMp[labelName] = [idx]
        labelMp = dict(sorted(labelMp.items(), key=lambda x: len(x[1]), reverse=True))
        
        # Create albums using the label map
        albumMp = {}
        vis = [False for i in range(len(allImageReqs))]
        for key,val in labelMp.items():
            for idx in val:
                if vis[idx]: continue
                if key in albumMp:
                    albumMp[key].append(idx)
                else:
                    albumMp[key] = [idx]
                vis[idx] = True

        # Insert new auto album entries and create new image tables
        for albumName, imageIdxList in albumMp.items():
            db.insertEntry(albumTableName, ALBUMINFO(albumName, 'auto'))
            autoImageTableName = accoID+'/'+albumName+'/'+mode+'/images'
            pKeyName = 'fileName'
            db.createTable(autoImageTableName, pKeyName)
            for idx in imageIdxList:
                req = allImageReqs[idx]
                fileName = req['S3Object']['Name']
                fileBucket = req['S3Object']['Bucket']
                imageInfo = db.readEntry(fileBucket, fileName, fileBucket)
                db.insertEntry(autoImageTableName, imageInfo)

        # Return the automatically created album names and their covers
        for albumName, _ in albumMp.items():
            autoImageTableName = accoID+'/'+albumName+'/'+mode+'/images'
            firstReq = allImageReqs[0]
            fileName = firstReq['S3Object']['Name']
            fileBucketName = firstReq['S3Object']['Bucket']
            bucket = s3client.Bucket(fileBucketName)
            firstItem = next(iter(bucket.objects.all()), None)
            fileFormat = fileName.split('.')[1]
            full_file_path = os.path.join(os_file_path, 'tmp.'+fileFormat)
            s3client.download_file(imageTableName, firstItem['Key'], full_file_path)
            coverImage = bytes.decode(base64.b64decode(Path(full_file_path).read_text()))
            covers.append({"albumName" : albumName, "coverImage" : coverImage})

    # Exiting the auto mode
    else:

        # Get manually created album covers
        albumTableName = accoID+'/albums'
        albumInfoList = db.readEntries(albumTableName, attriName='albumType', attriVal='manual')
        for albumInfo in albumInfoList:
            albumName      = albumInfo.albumName
            imageTableName = accoID+'/'+albumName+'/'+mode+'/images'
            bucket = s3client.Bucket(imageTableName)
            firstItem = next(iter(bucket.objects.all()), None)
            fileFormat = fileName.split('.')[1]
            full_file_path = os.path.join(os_file_path, 'tmp.'+fileFormat)
            s3client.download_file(imageTableName, firstItem['Key'], full_file_path)
            coverImage = bytes.decode(base64.b64decode(Path(full_file_path).read_text()))
            covers.append({"albumName" : albumName, "coverImage" : coverImage})        

    resp = {
        "success" : True,
        "covers"  : covers
    }
    response = webapp.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype='application/json'
    )
    return response

@webapp.route('/get_album_names', methods=['GET', 'POST'])
def get_album_names():
    """
    Get a list of names of the current albums
    Inputs:
        - 
    Outputs:
        - Album names [List]
    """ 

    # Lookup the album table of the user
    isAuto = session['isAuto']
    mode   = 'auto' if isAuto else 'manual'
    accoID = session['currentUser']
    albumTableName = accoID+'/albums'
    albumInfoList = db.readAllEntries(albumTableName)
    covers = []
    for albumInfo in albumInfoList:
        albumName = albumInfo.albumName
        imageTableName = accoID+'/'+albumName+'/'+mode+'/images'
        bucket = s3client.Bucket(imageTableName)
        firstItem = next(iter(bucket.objects.all()), None)
        coverImage = None
        if firstItem != None:
            fileName = os.path.basename(firstItem['Key'])
            fileFormat = fileName.split('.')[1]
            full_file_path = os.path.join(os_file_path, 'tmp.'+fileFormat)
            s3client.download_file(imageTableName, firstItem['Key'], full_file_path)
            coverImage = bytes.decode(base64.b64decode(Path(full_file_path).read_text()))
            covers.append({"albumName" : albumName, "coverImage" : coverImage})
    resp = {
        "success" : True,
        "covers"  : covers
    }
    response = webapp.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype='application/json'
    )
    return response

@webapp.route('/display_album', methods=['GET', 'POST'])
def display_album():

    """
    Display all images in an album
    Inputs:
        - Album name [String]
    Outputs:
        - A list of picture jsons [List]
    """
    # Get album name
    data = request.form
    albumName = str(data.get('album'))
    isAuto = session['isAuto']
    mode   = 'auto' if isAuto else 'manual'

    # Get all the image objects from their s3 buckets
    accoID = session['currentUser']
    imageTableName = accoID+'/'+albumName+'/'+mode+'/images'
    imageInfoList = db.readAllEntries(imageTableName)
    fileValues = []
    fileNames  = []
    for imageInfo in imageInfoList:
        fileName = imageInfo.fileName
        bucketName = imageInfo.fileBucket
        fileFormat = fileName.split('.')[1]
        full_file_path = os.path.join(os_file_path, 'tmp.'+fileFormat)
        s3client.download_file(bucketName, fileName, full_file_path)
        value = bytes.decode(base64.b64decode(Path(full_file_path).read_text()))
        fileValues.append(value)
        fileNames.append(fileName)

    resp = OrderedDict()
    files = [{'content' : fileValues[i], 'name' : fileNames[i]} for i in range(len(fileNames))]
    resp["images"] = files
    response = webapp.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype='application/json'
    )
    return response

@webapp.route('/sage_display_album', methods=['GET', 'POST'])
def sage_display_album():
    
    """
    Display all images in an album with target labels
    Inputs:
        - Album name [String]
        - key word [String]
    Outputs:
        - A list of picture jsons [List]
    """

    # Get album name and labels
    data         = request.form
    albumName    = str(data.get('album'))
    targetLabels = list(data.get('labels'))
    isAuto       = session['isAuto']
    mode         = 'auto' if isAuto else 'manual'

    # Get required images
    accoID = session['currentUser']
    imageTableName = accoID+'/'+albumName+'/'+mode+'/images'
    imageInfoList = db.readAllEntries(imageTableName)
    fileValues = []
    fileNames  = []
    for imageInfo in imageInfoList:
        fileName = imageInfo.fileName
        bucketName = imageInfo.fileBucket
        req  = {'S3Object': {'Bucket': bucketName, 'Name': fileName}}

        # detect labels in the image and get required images
        resp = rekclient.detect_labels(Image=req)
        for label in resp['Labels']:
            labelName = label['Name']
            if labelName in targetLabels:
                fileFormat = fileName.split('.')[1]
                full_file_path = os.path.join(os_file_path, 'tmp.'+fileFormat)
                s3client.download_file(imageTableName, fileName, full_file_path)
                value = bytes.decode(base64.b64decode(Path(full_file_path).read_text()))
                fileValues.append(value)
                fileNames.append(fileName)
                break

    resp = OrderedDict()
    resp["images"]    = fileValues[:]
    resp["fileNames"] = fileNames[:]
    response = webapp.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype='application/json'
    )
    return response

@webapp.route('/delete_album', methods=['GET', 'POST'])
def delete_manual_album():
    
    """
    Delete all images in an album
    Inputs:
        - Album name [String]
    Outputs:
        - Success / Fail [Boolean]
    """
    
    # Get album name
    data      = request.form
    albumName = str(data.get('album'))
    isAuto    = session['isAuto']
    mode      = 'auto' if isAuto else 'manual' 

    # Delete the image table and the album entry in the album table
    accoID = session['currentUser']
    albumTableName = accoID+'/albums'
    imageTableName = accoID+'/'+albumName+'/'+mode+'/images'
    db.deleteEntry(albumTableName, albumName)
    db.deleteTable(imageTableName)

    # Delete all the image objects from the s3 bucket and the bucket as well
    imageObjs = s3client.list_objects_v2(Bucket=imageTableName)
    for obj in imageObjs['Contents']:
        objKey = obj['Key']
        s3client.delete_object(Bucket=imageTableName, Key=objKey)
    s3client.delete_bucket(Bucket=imageTableName)
    
    resp = {
        "success" : True
    }
    response = webapp.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype='application/json'
    )
    return response

@webapp.route('/overwrite_manual_albums', methods=['GET', 'POST'])
def overwrite_manual_albums():

    """
    Use automatically created albums 
    Inputs:
        - 
    Outputs:
        - Success / Fail [Boolean]
    """
    accoID = session['currentUser']
    
    # Delete all the existing manual album entries and their image tables 
    albumTableName = accoID+'/albums'
    albumInfoList = db.readEntries(albumTableName, attriName='albumType', attriVal='manual')
    mode = 'manual'
    for albumInfo in albumInfoList:
        albumName = albumInfo.albumName
        imageTableName = accoID+'/'+albumName+'/'+mode+'/images'
        db.deleteTable(imageTableName)
    db.deleteEntries(albumTableName, attriName='albumType', attriVal='manual')

    # Change the types of all the albums to manual and update the names of all the image tables
    albumInfoList = db.readAllEntries(albumTableName)
    oldMode = 'auto'
    newMode = 'manual'
    for albumInfo in albumInfoList:
        albumName = albumInfo.albumName
        albumType = albumInfo.albumType
        db.deleteEntry(albumTableName,albumName,albumType)
        db.insertEntry(albumTableName,albumName,'manual')
        oldImageTableName = accoID+'/'+albumName+'/'+oldMode+'/images'
        newImageTableName = accoID+'/'+albumName+'/'+newMode+'/images'
        db.updateTable(oldImageTableName, newImageTableName, 'fileName')
    
    resp =  {
        'success' : True
    }
    response = webapp.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype='application/json'
    )
    return response


@webapp.route('/register', methods=['GET', 'POST'])
def create_account():
    """
    Create a new account
    Inputs:
        - Account Name [String]
        - Password     [String]
    Outputs:
        - Success / Fail [Boolean]
    """

    # Get account name and password
    data = request.form
    accoID = str(data.get('id'))
    passwd = str(data.get('password'))

    # Lookup the account from DB
    acco = db.readEntry('accounts', pKey=accoID)
    if acco != None:
        # Account already exists
        resp = {
            "success" : False,
            "message" : 'Account already exists :('
        }
        response = webapp.response_class(
            response=json.dumps(resp),
            status=400,
            mimetype='application/json'
        )
        return response
    
    # Insert the account to DB and login the new user if no current user
    db.insertEntry('accounts', ACCOUNTINFO(accoID, passwd))
    message = 'New account created :)'
    if session['loggedIn'] == False: # shoudl be always False
        session["currentUser"] = accoID
        session['loggedIn'] = True
        message += ' Automatically logged in :)'

    resp = {
        "success" : True,
        "message" : message
    }
    response = webapp.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype='application/json'
    )
    return response

@webapp.route('/login', methods=['GET', 'POST'])
def get_account():
    """
    Get an account
    Inputs:
        - Account Name [String]
        - Password     [String]
    Outputs:
        - Success / Fail [Boolean]
    """

    # Get account name and password
    data = request.form
    accoID = str(data.get('id'))
    passwd = str(data.get('password'))

    # Check if the current user is not logged out
    if session['loggedIn'] == True:
        # Current user is not logged out yet
        resp = {
            "success" : False,
            "message" : "Current user is not logged out yet :("
        }
        response = webapp.response_class(
            response=json.dumps(resp),
            status=400,
            mimetype='application/json'
        )
        return response

    # Lookup the account from DB
    acco = db.readEntry('accounts', pKey=accoID)
    if acco == None:
        # Account doesn't exist
        resp = {
            "success" : False,
            "message" : "Account name not found :("
        }
        response = webapp.response_class(
            response=json.dumps(resp),
            status=400,
            mimetype='application/json'
        )
        return response

    # Check password
    if passwd != acco.accoPasswd:
        # Password doesn't match
        resp = {
            "success" : False,
            "message" : "Wrong password :("
        }
        response = webapp.response_class(
            response=json.dumps(resp),
            status=400,
            mimetype='application/json'
        )
        return response

    # Logging in ...
    session["currentUser"] = accoID
    session["loggedIn"] = True
    resp = {
        "success" : True,
        "message" : "Logged in :)"
    }
    response = webapp.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype='application/json'
    )
    return response

@webapp.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    Get an account
    Inputs:
        - 
    Outputs:
        - Success / Fail [Boolean]
    """
    if session['loggedIn'] == False:
        # Current user is not logged out yet
        resp = {
            "success" : False,
            "message" : "No user is logged in yet :("
        }
        response = webapp.response_class(
            response=json.dumps(resp),
            status=400,
            mimetype='application/json'
        )
        return response
    
    # Logging out...
    session['loggedIn'] = False
    resp = {
        "success" : True,
        "message" : "Logged out :)"
    }
    response = webapp.response_class(
        response=json.dumps(resp),
        status=400,
        mimetype='application/json'
    )
    return response

