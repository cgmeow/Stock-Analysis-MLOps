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
        mode = "update"
        bucket = event['destination_bucket']
        key = event['destination_file']
        overwrite = event['overwrite']
        #convert overwrite to boolean
        if not 'data' in event or len(event['data']) == 0:
            mode = "download"
            source_bucket = event['source_bucket']
        if overwrite == "True":
            overwrite = True
        else:
            overwrite = False
        
        
        if key_exists(bucket,key) == False:
            return {
            'statusCode': 404,
            'body': json.dumps(f'Error: filepath s3://{bucket}/{key} not found.')
        }
    
        object = s3_client.get_object(Bucket=bucket, Key=key)
        body = object['Body']
        source_csv_string = body.read().decode('utf-8')
        df = pd.read_csv(StringIO(source_csv_string))
        
        if mode == "download":
            if not 'retrieve_date' in event or len(event['retrieve_date']) == 0:
                retrieve_date = str(date.today())
            else:
                retrieve_date = event['retrieve_date']
            print(retrieve_date)
            source_key = f'webscrape_{retrieve_date}.csv'
            if key_exists(source_bucket,source_key) == False:
                return {
                'statusCode': 404,
                'body': json.dumps(f'Error: filepath s3://{source_bucket}/{source_key} not found.')
            }
            source_object = s3_client.get_object(Bucket=source_bucket, Key=source_key)
            source_body = source_object['Body']
            source_csv_string = source_body.read().decode('utf-8')
            source_df = pd.read_csv(StringIO(source_csv_string))
            source_df.drop_duplicates(inplace=True)
            source_df['Date'] = pd.to_datetime(source_df['Date'])
            source_df['Date'] = source_df['Date'].dt.strftime('%d/%m/%Y')
            source_df = source_df.rename(columns={'Stock': 'STOCK'})
            
        else:
            source_df = pd.DataFrame(event['data'])
            print(source_df)
            for col in source_df.columns:
                if col not in df.columns:
                    return {
                        'statusCode': 400,
                        'body': json.dumps(f'Error: Column {col} not found in destination file.')
                    }
            
            for col in df.columns:
                if col not in source_df.columns:
                    return {
                        'statusCode': 400,
                        'body': json.dumps(f'Error: Column {col} not found in source file.')
                    }
                    
        # source_df['Close_7_Days'] = "NAN"
        filtered_df = df[(df['STOCK'].isin(source_df['STOCK'])) & (df['Date'].isin(source_df['Date']))]
        
        if not filtered_df.empty:
            if overwrite:
                df = df[~df.isin(filtered_df)].dropna()
                df = pd.concat([df,source_df], ignore_index=True)
            else:
                return {
                    'statusCode': 400,
                    'body': json.dumps(f'Error: Data already exists in destination file.'),
                    'error_cases':json.dumps(filtered_df.to_dict(orient='records'))
                }
        else:
            df = pd.concat([df,source_df], ignore_index=True)
            
        # Write Next 7 Days Close Value
        # helper_df = df[['Date','Close']]
        # helper_df['Date'] = (pd.to_datetime(helper_df['Date']) - pd.Timedelta(days=7)).dt.strftime('%d/%m/%Y')
        # helper_df.rename(columns = {'Close':'Close_7_Days'}, inplace=True)
        # df.drop('Close_7_Days',axis=1, inplace=True)
        # df = df.merge(helper_df,how='left',on='Date')
        # # df.drop_duplicates()
        # # df.fillna("NAN")
        # print(df.head(10))
        
        
        
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
        'body': json.dumps("File Updated")
    }