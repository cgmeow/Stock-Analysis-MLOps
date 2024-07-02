import boto3
import json
import botocore
from io import StringIO
import pandas as pd
from datetime import datetime, timedelta

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

def find_sentiment_rating(sentiment):
    if sentiment < -0.5:
        return "Very Bad"
    if sentiment >=-0.5 and sentiment < 0:
        return "Bad"
    if sentiment ==0:
        return "Netural"
    if sentiment > 0  and sentiment <=0.5:
        return "Good"
    if sentiment > 0.5:
        return "Very Good"


def load_df_from_s3(bucket, key):
    object = s3_client.get_object(Bucket=bucket, Key=key)
    body = object['Body']
    csv_string = body.read().decode('utf-8')
    df = pd.read_csv(StringIO(csv_string))
    return df

# Boto Update Job from S3
def lambda_handler(event, context):
    # try:
    stock = event['stock']
    bucket = event['s3_bucket_name']
    key = event['source_file']
    if not "limit" in event or len(event["limit"]) == 0:
        limit = 10
    else:
        limit = event['limit']
    current_date = datetime.now()
    
    for _ in range(limit):
        file = key + current_date.strftime('%Y-%m-%d')+".csv"
        if key_exists(bucket,file):
            print(file)
            break
        current_date = current_date - timedelta(days=1)
        
    print(file)
    
    df = load_df_from_s3(bucket,file)

    # Get df_value
    df = df[df['Stock'] == stock]
    df['Sentiment'] = df['SentimentScore'].apply(find_sentiment_rating)

    # write to json
    data_dict = df.to_dict(orient='records')
    #print(data_dict[0])


    # except Exception as e:
    #     return {
    #     'statusCode': 500,
    #     'body': json.dumps(f'Error: {e}')
    # }

    return {
        'statusCode': 200,
        'date_retrieved':current_date.strftime('%Y-%m-%d'),
        'body': json.dumps(data_dict)
    }