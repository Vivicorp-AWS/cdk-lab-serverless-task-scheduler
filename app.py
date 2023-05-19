#!/usr/bin/env python3
import os

import aws_cdk as cdk

from stacks.lambda_stack import LambdaStack
from stacks.sqs_stack import SQSStack
from stacks.scheduler_stack import SchedulerStack

app = cdk.App()

PREFIX = app.node.try_get_context("prefix")

sqs_stack = SQSStack(
    app, f"{PREFIX}-sqs",
    description="CDK Lab SQS Stack",
)

queue = sqs_stack.queue

lambda_stack = LambdaStack(
    app, f"{PREFIX}-lambda",
    queue=queue,
    description="CDK Lab Lambda Layer Stack",
    )

lambda_sendtask = lambda_stack.lambda_sendtask

scheduler_stack = SchedulerStack(
    app, f"{PREFIX}-scheduler",
    lambdafn=lambda_sendtask,
    description="CDK Lab Scheduler Stack",
)

app.synth()
