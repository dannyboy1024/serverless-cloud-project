# TODO: Add background processing...
# CPU Utilizations...
import psutil
import time
import json
import boto3
import math
from datetime import datetime
from config import Config


#convert mins to datetime obj - not working as expected 
def convert_unix_to_utc(unix_in_min):
	ts = int(unix_in_min * 60)
	return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

# lambda client
lambda_client = boto3.client('lambda')

# data collection
# cpu_util, mem_util, disk_util, all in percentage
while True:
	time_stamp = math.floor(time.time() / 60)
	data = {}
	cpu_util = psutil.cpu_percent(interval=None)
	mem_util = psutil.virtual_memory()
	mem_util = mem_util.percent
	disk_util = psutil.disk_usage('/')
	disk_util = disk_util.percent
	data['timestamp'] = time_stamp
	data['Metrics'] = {}
	data['Metrics']['CPU_Usage'] = cpu_util
	data['Metrics']['Mem_Usage'] = mem_util
	data['Metrics']['Disk_Usage'] = disk_util
	json_data = json.dumps(data, sort_keys=True, default=str)

	print(json_data)

	# invoke lambda
	response = lambda_client.invoke(FunctionName='uploadPMToDynamo', Payload= json_data)

	print(response)
	time.sleep(60)