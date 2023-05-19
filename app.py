#!/usr/bin/env python3
import os

import aws_cdk as cdk

from stacks.lambda_stack import LambdaStack
from stacks.sqs_stack import SQSStack
from stacks.scheduler_stack import SchedulerStack

app = cdk.App()

sqs_stack = SQSStack(
    app, "cdklab-sqs",
    description="CDK Lab SQS Stack",
)

queue = sqs_stack.queue

lambda_stack = LambdaStack(
    app, "cdklab-lambda",
    queue=queue,
    description="CDK Lab Lambda Layer Stack",
    )

lambda_sendtask = lambda_stack.lambda_sendtask

scheduler_stack = SchedulerStack(
    app, "cdklab-scheduler",
    lambdafn=lambda_sendtask,
    description="CDK Lab Scheduler Stack",
)

app.synth()
