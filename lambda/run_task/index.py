# Blank Lambda function ref: https://github.com/awsdocs/aws-lambda-developer-guide/blob/main/sample-apps/blank-python/function/lambda_function.py
# SQS sample code ref: https://docs.aws.amazon.com/lambda/latest/dg/with-sqs-create-package.html#with-sqs-example-deployment-pkg-python
import logging
import os
import boto3  # type: ignore
import jsonpickle  # type: ignore

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs = boto3.client('sqs')

def handler(event, context):    
    logger.info('## ENVIRONMENT VARIABLES\r' + jsonpickle.encode(dict(**os.environ)))
    logger.info('## EVENT\r' + jsonpickle.encode(event))
    logger.info('## CONTEXT\r' + jsonpickle.encode(context))
    
    for record in event['Records']:
        print("Task received:")
        payload = record["body"]
        print(str(payload))