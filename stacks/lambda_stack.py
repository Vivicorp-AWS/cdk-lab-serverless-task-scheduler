from aws_cdk import (
    aws_lambda as _lambda,
    RemovalPolicy,
    Stack,
    Duration,
    CfnOutput,
)
from constructs import Construct


class LambdaLayerStack(Stack):
    def __init__(
            self,
            scope: Construct,
            id: str,
            role_lambda_sendmessage,
            **kwargs,) -> None:
        super().__init__(scope, id, **kwargs)

        # Python Lambda layer for send-message-lambda-function Lambda function
        layer_sendmessage = _lambda.LayerVersion(
            self, 'send-message-lambda-layer',
            description='Python layer for send-message-lambda-function',
            code=_lambda.Code.from_asset("layer"),
            compatible_runtimes=[
                _lambda.Runtime.PYTHON_3_8,
                _lambda.Runtime.PYTHON_3_9,
                _lambda.Runtime.PYTHON_3_10],
            removal_policy=RemovalPolicy.DESTROY
            )

        # Lambda function for sending message
        lambda_sendmessage = _lambda.Function(
            self, "send-message-lambda-function",
            description="Function to send message to IM applications",
            code=_lambda.Code.from_asset("lambda"),
            handler="index.handler",
            runtime=_lambda.Runtime.PYTHON_3_10,
            layers=[layer_sendmessage],
            role=role_lambda_sendmessage,
            timeout=Duration.seconds(15),
            )

        # [TODO] Add SQS as event source
        # queue = sqs.Queue(self, "MyQueue")
        # event_source = SqsEventSource(queue)
        # fn.add_event_source(event_source)

        CfnOutput(self, "SendMessageFunctionARN", value=lambda_sendmessage.function_arn,)
        CfnOutput(self, "SendMessageFunctionName", value=lambda_sendmessage.function_name,)
