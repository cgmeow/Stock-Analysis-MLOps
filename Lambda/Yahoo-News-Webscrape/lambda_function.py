import boto3
import json
import time

ec2 = boto3.client('ec2')
ssm = boto3.client('ssm')

def lambda_handler(event, context):
    if not 'stock_list' in event:
        stock_list = 'all'
    else:
        stock_list = json.dumps(event['stocks'])
    instance_id = 'i-0242760bdfc72d666'
    s3_bucket_name = 'mle-webscrape-runlog-dumps'
    s3_log_file = 'ec2_script_output.log'
    command = f'''#!/bin/bash
                  sudo apt-get update
                  sudo apt-get install -y python3-pip awscli
                  echo "import sys\nimport boto3\ns3 = boto3.client('s3')\nbucket = '{s3_bucket_name}'\nlog_file = '{s3_log_file}'\nwith open('/tmp/log.txt', 'w') as f:\n    sys.stdout = f\n    sys.stderr = f\n    print('Hello from EC2!')\n    print('This will be logged and uploaded to S3.')\n    f.seek(0)\n    s3.upload_file('/tmp/log.txt', bucket, log_file)" > /home/ubuntu/your_script.py
                  sudo service amazon-ssm-agent start
                  python3 /home/ec2-user/Yahoo_Finance_News_Webscrape_EC2.py {stock_list}
                  '''

    # Start the instance
    ec2.start_instances(InstanceIds=[instance_id])

    # Wait for the instance to be running
    waiter = ec2.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])
    time.sleep(10) # Adjust sleep time as needed
    
    print(f"{instance_id} Instance Started")
    # Send the command to run the script
    response = ssm.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={'commands': [command]}
    )
    
    command_id = response['Command']['CommandId']
    
    # Wait for the command to complete
    time.sleep(10)  # Adjust sleep time as needed
    waiter = ssm.get_waiter('command_executed')
    waiter.wait(CommandId=command_id, InstanceId=instance_id, WaiterConfig={'Delay': 1000,
        'MaxAttempts': 1000}
        )

    print("Command Yahoo_Finance_Data_Webscrape.py Complete")

    # Stop the instance
    ec2.stop_instances(InstanceIds=[instance_id])
    
    print(f"{instance_id} Instance Stopped")

    return {
        'statusCode': 200,
        'body': json.dumps(f'Instance {instance_id} started, script executed, and instance stopped for stock_list = {stock_list}')
    }
