# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import csv
import json
import boto3
import sys

params = json.loads(sys.argv[1])
filename = params['filename']

# connect to AWS--------------
aws_id = 'AKIA5IM6XOLZZJTX5VPN'
aws_secret = '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'
s3 = boto3.client('s3', aws_access_key_id=aws_id, aws_secret_access_key=aws_secret)
bucket= 'application-aws-version'
file_path = "control_group_selection/"+filename
obj = s3.get_object(Bucket= bucket, Key= file_path)
body = obj['Body']
csv_content = body.read().decode('utf-8').splitlines()
csv_data = csv.DictReader(csv_content)
json_data = []
for csv_row in csv_data:
    json_data.append(csv_row)
jsonString = json.dumps(json_data)
data = pd.read_json(jsonString)
data.head()

#------------- output list for the user ---------------------

cat_var_list=[]
for col in range(0,data.shape[1]): 
  cat_var_list.append(data.columns[col])

json=json.dumps(cat_var_list, indent=4) 
print(json)


