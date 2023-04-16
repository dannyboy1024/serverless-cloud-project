# TODO: Add background processing...
# CPU Utilizations...
import psutil
import time
import json
import boto3
from datetime import datetime

# lambda client
boto_session = boto3.Session(
    aws_access_key_id = 'AKIAXHQE6ZG47G5N5PDN',
    aws_secret_access_key = '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',
    region_name='us-east-1'
)

lambda_client = boto_session.client('lambda')
lambda_functions = lambda_client.list_functions()
print(lambda_functions)

# data collection
# cpu_util, mem_util, disk_util, all in percentage
while True:
	now = datetime.now()
	time_stamp = now.strftime("%Y/%m/%d, %H:%M:%S")
	data = {}
	cpu_util = psutil.cpu_percent(interval=None)
	mem_util = psutil.virtual_memory()
	mem_util = mem_util.percent
	disk_util = psutil.disk_usage('/')
	disk_util = disk_util.percent
	data['timestamp'] = str(time_stamp)
	data['Metrics'] = {}
	data['Metrics']['CPU_Usage'] = str(cpu_util)
	data['Metrics']['Mem_Usage'] = str(mem_util)
	data['Metrics']['Disk_Usage'] = str(disk_util)
	json_data = json.dumps(data, sort_keys=True, default=str)

	print(json_data)

	# invoke lambda
	response = lambda_client.invoke(FunctionName='uploadPMToDynamo', Payload=json_data)
	results = response['Payload'].read()

	print(response)
	print(results)
	time.sleep(30)