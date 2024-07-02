import boto3
import json
import botocore
from io import StringIO
import pandas as pd
from datetime import datetime

s3_client = boto3.client('s3')

def key_exists(bucket, key):
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            # The key does not exist
            return False
        else:
            # Something else has gone wrong
            raise
    else:
        # The key does exist
        return True


# Boto Update Job from S3
def lambda_handler(event, context):
    try:
        stock = event['stock']
        bucket = event['s3_bucket_name']
        key = event['source_file']
        if not 'records' in event:
            records = 5
        else:
            records = event['records']
        
        if key_exists(bucket,key) == False:
            return {
            'statusCode': 404,
            'body': json.dumps(f'Error: filepath s3://{bucket}/{key} not found.')   
        }
    
        object = s3_client.get_object(Bucket=bucket, Key=key)
        body = object['Body']
        source_csv_string = body.read().decode('utf-8')
        df = pd.read_csv(StringIO(source_csv_string))
        
        
        # filter start date and end date, and Stock\
        # print(df['Date'].head(3))
        df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y %H:%M")
        df = df[df['Stock'] == stock]
        # Get latest news headlines
        df = df.sort_values(by='Date', ascending=False)
        df = df.head(records)
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d %H:%M')
        df = df[['Title','URL']]
    
        # write to json
        data_dict = df.to_dict(orient='records')


    except Exception as e:
        return {
        'statusCode': 500,
        'body': json.dumps(f'Error: {e}')
    }

    return {
        'statusCode': 200,
        'body': json.dumps(data_dict)
    }