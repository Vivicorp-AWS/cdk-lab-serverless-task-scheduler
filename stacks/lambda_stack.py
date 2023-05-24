from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_logs as logs,
    RemovalPolicy,
    Duration,
    CfnOutput,
)
from aws_cdk.aws_lambda_event_sources import SqsEventSource
from constructs import Construct
import os

class LambdaStack(Stack):
    def __init__(
            self,
            scope: Construct,
            id: str,
            queue,
            **kwargs,) -> None:
        super().__init__(scope, id, **kwargs)

        # Python Lambda layer for Lambda functions
        layer = _lambda.LayerVersion(
            self, 'send-task-lambda-layer',
            description='Python layer for send-task-lambda-function"',
            code=_lambda.Code.from_asset("layer"),
            compatible_runtimes=[
                _lambda.Runtime.PYTHON_3_8,
                _lambda.Runtime.PYTHON_3_9,
                _lambda.Runtime.PYTHON_3_10],
            removal_policy=RemovalPolicy.DESTROY
            )
        
        # Policy for receiving and deleting messages from SQS
        # [NOTE] The send message action is written in the code by ourselves,
        # CDK won't know that, so it's necessary to create a policy for it
        # and attach it to the role manually.
        policy_sendtask = iam.Policy(
            self, "SendtoSQSPolicy",
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "sqs:SendMessage",
                    ],
                    resources=[queue.queue_arn]
                ),
            ],
        )

        # Lambda function for sending task to the queue
        self.lambda_sendtask = _lambda.Function(
            self, "send-task-lambda-function",
            description="Function to send task to queue",
            code=_lambda.Code.from_asset(os.path.join(os.curdir, "lambda", "send_task")),
            environment={"QUEUE_URL": queue.queue_url},
            handler="index.handler",
            runtime=_lambda.Runtime.PYTHON_3_10,
            layers=[layer],
            log_retention=logs.RetentionDays.ONE_WEEK,
            timeout=Duration.seconds(30),
            # tracing=_lambda.Tracing.ACTIVE,  # X-Ray Tracing
            )
        self.lambda_sendtask.role.attach_inline_policy(policy_sendtask)
        
        # Lambda function for reading task from the queue
        self.lambda_runtask = _lambda.Function(
            self, "run-task-lambda-function",
            description="Function to read task from queue and execute",
            code=_lambda.Code.from_asset(os.path.join(os.curdir, "lambda", "run_task")),
            handler="index.handler",
            runtime=_lambda.Runtime.PYTHON_3_10,
            layers=[layer],
            log_retention=logs.RetentionDays.ONE_WEEK,
            timeout=Duration.minutes(1),
            # tracing=_lambda.Tracing.ACTIVE,  # X-Ray Tracing
            )
        
        # Add SQS as event source
        event_source_queue = SqsEventSource(queue, batch_size=1,)
        self.lambda_runtask.add_event_source(event_source_queue)

        CfnOutput(self, "SendTaskLambdaFunctionARN", value=self.lambda_sendtask.function_arn,)
        CfnOutput(self, "SendTaskLambdaFunctionName", value=self.lambda_sendtask.function_name,)
        CfnOutput(self, "SendTaskLambdaFunctionServiceRoleName", value=self.lambda_sendtask.role.role_name,)
        CfnOutput(self, "SendTaskLambdaFunctionServiceRoleARN", value=self.lambda_sendtask.role.role_arn,)
        CfnOutput(self, "RunTaskLambdaFunctionARN", value=self.lambda_runtask.function_arn,)
        CfnOutput(self, "RunTaskLambdaFunctionName", value=self.lambda_runtask.function_name,)
        CfnOutput(self, "RunTaskLambdaFunctionServiceRoleName", value=self.lambda_runtask.role.role_name,)
        CfnOutput(self, "RunTaskLambdaFunctionServiceRoleARN", value=self.lambda_runtask.role.role_arn,)
