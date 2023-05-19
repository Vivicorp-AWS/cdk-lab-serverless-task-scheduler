import os
import boto3
import requests
import json

QUEUE_URL = os.environ["QUEUE_URL"]
sqs = boto3.client('sqs')
# [TODO] Isolate the tasks' content from here to another document
msgs = ["Hello from Lambda #1!", "Hello from Lambda #2!"]

# [TODO] Add Logging
def handler(event, context):
    for msg in msgs:
        response = sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=(msg),
            MessageGroupId='1337',
        )
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps("Message(s) sent successfully", indent=4, sort_keys=True),
    }