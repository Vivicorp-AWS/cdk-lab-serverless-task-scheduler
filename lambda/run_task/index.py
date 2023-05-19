import os
import boto3
import requests
import json

sqs = boto3.client('sqs')
# [TODO] Isolate the tasks' content from here to another document
msgs = ["Hello from Lambda #1!", "Hello from Lambda #2!"]

# [TODO] Add Logging
def handler(event, context):    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps("Message(s) received successfully", indent=4, sort_keys=True),
    }