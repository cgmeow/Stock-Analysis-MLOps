import boto3
import json
import botocore
from io import StringIO
import pandas as pd
from datetime import datetime, timedelta
import requests
import numpy as np


sagemaker_client = boto3.client('sagemaker-runtime')
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


def load_df_from_s3(bucket, key):
    object = s3_client.get_object(Bucket=bucket, Key=key)
    body = object['Body']
    csv_string = body.read().decode('utf-8')
    df = pd.read_csv(StringIO(csv_string))
    return df
    
def invoke_sagemaker_endpoint(endpoint_name,payload):
    response = sagemaker_client.invoke_endpoint(
        EndpointName = endpoint_name,
        ContentType = "text/csv",
        Body = payload
    )
    result = response['Body'].read().decode('utf-8')
    return result
    
    
# Boto Update Job from S3
def lambda_handler(event, context):
    try:
        endpoint_name = event['sm_finance_endpoint_name']
        bucket = event['s3_source_bucket_name']
        key = event['source_file']
        inference_bucket = event["s3_dest_bucket_name"]
        inference_key = event["dest_file"]
        
        
        df = load_df_from_s3(bucket, key)
        # print(df.head(10))
        
        df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y")
        df.drop(columns=['Close_7_Days'], inplace = True)
        
        end_date = df['Date'].max()
        
        
        inference_df = load_df_from_s3(inference_bucket,inference_key)
        inference_df['Date'] = pd.to_datetime(inference_df['Date'], format="%d/%m/%Y")
        
        # Find Most Recent Datapoint
        filtered_df = inference_df[inference_df['Date']==end_date]
        
        # print(filtered_df)
        
        
        
        if not filtered_df.empty:
            return {
                    'statusCode': 400,
                    'body': json.dumps(f'Error: Data already exists in destination file.'),
                    'error_cases':json.dumps(filtered_df.to_dict(orient='records'))
                    }
        
        new_data_df = df[df['Date']==end_date]
        sub_inference_df = df[df['Date']==end_date]
        sub_inference_df = sub_inference_df[['STOCK','Date']]
        sub_inference_df = sub_inference_df.rename(columns={'STOCK':'Stock'})
        
        new_data_df.drop(columns=['Date'], inplace = True)
        new_data_df['Volume'] = new_data_df['Volume'].str.replace(',','').astype(float)
        new_data_df = new_data_df.replace(['AAPL','AMD','AMZN','GOOG','META','MSFT','NVDA'],[0,1,2,3,4,5,6])
        
        payload = new_data_df.to_csv(header=False, index = False)
        result = invoke_sagemaker_endpoint(endpoint_name = endpoint_name, payload = payload)
        df_output = pd.DataFrame(result.split('\n')[:-1])
        sub_inference_df['Prediction Date'] = sub_inference_df['Date'] + timedelta(days=7)
        sub_inference_df['Date'] = sub_inference_df['Date'].dt.strftime('%d/%m/%Y')
        sub_inference_df['Prediction Date'] = sub_inference_df['Prediction Date'].dt.strftime('%d/%m/%Y')
        
        sub_inference_df.reset_index(inplace=True)
        df_output.reset_index(inplace=True)
        sub_inference_df = sub_inference_df.merge(df_output,left_index=True, right_index=True)
        sub_inference_df=sub_inference_df.drop(columns=['index_x', 'index_y'])
        sub_inference_df = sub_inference_df.rename(columns={0:'Infered Close'})
        
        inference_df['Date'] = inference_df['Date'].dt.strftime('%d/%m/%Y')
        #test_df = inference_df.head(10)
        inference_df = pd.concat([sub_inference_df,inference_df], ignore_index = "True")
        print(inference_df)
        
        # Replace the destination file with the updated data
        csv_file = '/tmp/output.csv'
        inference_df.to_csv(csv_file, index =False)
        
        s3_client.upload_file(csv_file, inference_bucket, inference_key)
        
    except Exception as e:
        return {
        'statusCode': 500,
        'body': json.dumps(f'Error: {e}')
    }

    return {
        'statusCode': 200,
        'body': json.dumps("File Updated")
    }