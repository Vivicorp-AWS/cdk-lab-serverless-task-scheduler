# Blank Lambda function ref: https://github.com/awsdocs/aws-lambda-developer-guide/blob/main/sample-apps/blank-python/function/lambda_function.py
import logging
import os
import boto3  # type: ignore
import jsonpickle  # type: ignore

logger = logging.getLogger()
logger.setLevel(logging.INFO)

queue_url = os.environ["QUEUE_URL"]
sqs = boto3.client('sqs')
tasks = ["Hello from Lambda #1!", "Hello from Lambda #2!"]
logger.info('## TASKS\r' + jsonpickle.encode(tasks))

def handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES\r' + jsonpickle.encode(dict(**os.environ)))
    logger.info('## EVENT\r' + jsonpickle.encode(event))
    logger.info('## CONTEXT\r' + jsonpickle.encode(context))

    # Send tasks to queue
    for task in tasks:
        try:
            response = sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=(task),
                MessageGroupId='1337',
            )
            logger.info('## SQS RESPONSE\r' + jsonpickle.encode(response))
        except Exception as e:
            logger.error(e)
            raise e
    