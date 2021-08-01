# -*- coding: utf-8 -*-
"""
Created on Sat Jul  3 18:36:24 2021

@author: AHAB2
"""

import boto3
import json
from boto3.session import Session

prefix      = "user1/input_data"

ACCESS_KEY='AKIA5IM6XOLZZJTX5VPN'
SECRET_KEY='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'

session = Session(aws_access_key_id=ACCESS_KEY,
                  aws_secret_access_key=SECRET_KEY)
s3 = session.resource('s3')
my_bucket = s3.Bucket('application-aws-version')


files_list=[]
for object_summary in my_bucket.objects.filter(Prefix="user1/input_data/"):
    file_name=object_summary.key[len(prefix)+1:]
    #print(file_name)
    if(file_name !=""):
        files_list.append(file_name)

json=json.dumps(files_list, indent=4) 
print(json)