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


def load_df_from_s3(bucket, key):
    object = s3_client.get_object(Bucket=bucket, Key=key)
    body = object['Body']
    csv_string = body.read().decode('utf-8')
    df = pd.read_csv(StringIO(csv_string))
    return df

# Boto Update Job from S3
def lambda_handler(event, context):
    try:
        mode = ""
        stock = event['stock']
        bucket = event['s3_bucket_name']
        key = event['source_file']
        if not 'date_range' in event or len(event['date_range']) == 0:
            mode = "latest"
        elif len(event['date_range']) != 2:
            return {
                'statusCode': 400,
                'body': json.dumps(f'Error: date_range must have 2 elements.')
            }
        elif not 'inference_bucket' in event or not 'inference_key' in event:
            return {
                'statusCode': 400,
                'body': json.dumps(f'Error: inference_bucket and inference_key must be provided.')
            }
        else:
            date_range = event['date_range']
            #print(date_range[0],date_range[1])
            start_date = datetime.strptime(date_range[0],"%d/%m/%Y")
            end_date = datetime.strptime(date_range[1],"%d/%m/%Y")
            inference_bucket = event['inference_bucket']
            inference_key = event['inference_key']
    
        
        if key_exists(bucket,key) == False:
            return {
            'statusCode': 404,
            'body': json.dumps(f'Error: filepath s3://{bucket}/{key} not found.')
        }
    

        df = load_df_from_s3(bucket, key)
        
        
        # filter start date and end date, and Stock
        df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y")
        if mode == "latest":
            df = df[df['Date'] == df['Date'].max()]
        else:
            df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
        df = df[df['STOCK'] == stock]
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
        # drop the stock column
        df.drop(columns=['STOCK'], inplace=True)
        df.drop(columns=['Close_7_Days'], inplace = True)

        max_date = df['Date'].max()
        print(max_date)
        
        if mode != "latest": # Data is used for charting
            # Find future Inference data.
            
            inference_df = load_df_from_s3(inference_bucket, inference_key)
            
            inference_df['Prediction Date'] = pd.to_datetime(inference_df['Prediction Date'], format="%d/%m/%Y")
            inference_df = inference_df[inference_df['Stock'] == stock]
            inference_df.drop(columns=['Date'], inplace=True)
            # Rename columns
            inference_df.rename(columns={"Infered Close": "Close","Prediction Date": "Date"}, inplace=True)
            # print(inference_df.columns)
            
            inference_df = inference_df[inference_df['Date'] > max_date]
            inference_df['Date'] = inference_df['Date'].dt.strftime('%Y-%m-%d')
            inference_df.drop(columns=['Stock'], inplace=True)
            df['Inference'] = "N"
            inference_df['Inference'] = "Y"
            #inference_df.fillna(0,inplace  =True)
            

            # print(inference_df)

            # Append Inference data to the end of the dataframe
            
            df = pd.concat([df,inference_df], ignore_index=True)
            
        
        # write to json
        df = df.sort_values(by='Date')
        df.fillna(0,inplace = True)
        data_dict = df.to_dict(orient='records')
        #print(data_dict[0])


    except Exception as e:
        return {
        'statusCode': 500,
        'body': json.dumps(f'Error: {e}')
    }

    return {
        'statusCode': 200,
        'body': json.dumps(data_dict)
    }