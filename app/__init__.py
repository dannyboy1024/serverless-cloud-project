import os
from flask import Flask
from flask_cors import CORS
import boto3


webapp = Flask(__name__)
CORS(webapp)
from app import main