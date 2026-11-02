import boto3
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
dt=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# s3 = boto3.client('s3')
key=(
    f"company_doc/"
    f"{dt.year}/"
    f"{dt.month:02d}/"
    f"{dt.day:02d}/"
    f"{detection['camera_id']}/"
    f"{dt.strftime('%Y%m%dT%H%M%SZ')}_{detection['id']}.json"
)

s3=boto3.client(
    's3',
    region_name='ap-south-1',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),

)
response = s3.list_buckets()
for bucket in response['Buckets']:
    print(bucket['Name'])