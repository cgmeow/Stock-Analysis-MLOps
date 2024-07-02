import boto3
import json
import botocore
from io import StringIO
import pandas as pd
from datetime import datetime, date


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
        bucket = event['destination_bucket']
        key = event['destination_file']
        #convert overwrite to boolean
        source_bucket = event['source_bucket']
        if not "stock_list" in event or len(event['stock_list']) == 0:
            stock_list =['META', 
                        'AAPL', 
                        'GOOG', 
                        'AMZN', 
                        'MSFT', 
                        'NVDA', 
                        'AMD']
        else:
            stock_list = event['stock_list'].split(',')
    
        
        if key_exists(bucket,key) == False:
            return {
            'statusCode': 404,
            'body': json.dumps(f'Error: filepath s3://{bucket}/{key} not found.')
        }
    
        object = s3_client.get_object(Bucket=bucket, Key=key)
        body = object['Body']
        source_csv_string = body.read().decode('utf-8')
        df = pd.read_csv(StringIO(source_csv_string))
        
        if not 'retrieve_date' in event or len(event['retrieve_date']) == 0:
            retrieve_date = str(date.today())
        else:
            retrieve_date = event['retrieve_date']
        success= []
        failed = []
        for stock in stock_list:
            source_key = f'news_data_{stock}_{retrieve_date}.csv'
            if key_exists(source_bucket,source_key) == False:
                failed.append(f"s3://{source_bucket}/{source_key}")
                continue
            source_object = s3_client.get_object(Bucket=source_bucket, Key=source_key)
            source_body = source_object['Body']
            source_csv_string = source_body.read().decode('utf-8')
            source_df = pd.read_csv(StringIO(source_csv_string))
            # if Date column is "No date available", remove it
            source_df = source_df[source_df['Date'] != 'No date available']
            # Convert the date to the correct format
            source_df['Date'] = pd.to_datetime(source_df['Date'])
            source_df['Date'] = source_df['Date'].dt.strftime('%d/%m/%Y %H:%M')
        
            
            df = pd.concat([df,source_df], ignore_index=True)
            df.drop_duplicates(inplace=True)
            success.append(f"s3://{source_bucket}/{source_key}")
            
        
        # Replace the destination file with the updated data
        csv_file = '/tmp/output.csv'
        df.to_csv(csv_file, index =False)
    
        s3_client.upload_file(csv_file, bucket, key)



    except Exception as e:
        return {
        'statusCode': 500,
        'body': json.dumps(f'Error: {e}')
    }

    return {
        'statusCode': 200,
        'body': json.dumps("File Updated"),
        'success':json.dumps(success),
        'failed': json.dumps(failed)
    }