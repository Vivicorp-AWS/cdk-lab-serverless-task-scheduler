#!/usr/bin/env python3
import os

import aws_cdk as cdk

from stacks.iam_stack import IAMStack
from stacks.lambda_stack import LambdaLayerStack


app = cdk.App()

lambda_stack = IAMStack(
    app, "cdklab-iam",
    #env=cdk.Environment(account='123456789012', region='us-east-1'),
    description="CDK Lab IAM Stack",
    )

role_lambda_sendmessage = lambda_stack.role_lambda_sendmessage

lambda_stack = LambdaLayerStack(
    app, "cdklab-lambda",
    #env=cdk.Environment(account='123456789012', region='us-east-1'),
    description="CDK Lab Lambda Layer Stack",
    role_lambda_sendmessage=role_lambda_sendmessage,
    )

app.synth()
