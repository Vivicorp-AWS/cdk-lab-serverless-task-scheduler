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
        
        # Service role for send-message-lambda-function
        role_lambda_sendtask = iam.Role(self, "SendTaskLambdaServiceRole",
            description="Service role for send-task-lambda-function",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )

        # Service role for read-message-lambda-function
        role_lambda_runtask = iam.Role(self, "RunTaskLambdaServiceRole",
            description="Service role for run-task-lambda-function",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )

        # Policy for managing CloudWatch Logs
        policy_manage_logs = iam.Policy(
            self, "ManageCloudWatchLogsPolicy",
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                    ],
                    resources=["*"]
                ),
            ],
        )

        # Policy for receiving and deleting messages from SQS
        policy_sendtask = iam.Policy(
            self, "SendtoSQSPolicy",
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "sqs:SendMessage",
                    ],
                    resources=[queue.queue_arn]  # [TODO] Inject SQS Queue
                ),
            ],
        )

        # Policy for receiving and deleting messages from SQS
        policy_runtask = iam.Policy(
            self, "ReadfromSQSPolicy",
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "sqs:ReceiveMessage",
                        "sqs:DeleteMessage",
                        "sqs:GetQueueAttributes",
                    ],
                    resources=[queue.queue_arn]  # [TODO] Inject SQS Queue
                ),
            ],
        )

        role_lambda_sendtask.attach_inline_policy(policy_manage_logs)
        role_lambda_sendtask.attach_inline_policy(policy_sendtask)
        role_lambda_runtask.attach_inline_policy(policy_manage_logs)
        role_lambda_runtask.attach_inline_policy(policy_runtask)

        # Lambda function for sending task to queue
        self.lambda_sendtask = _lambda.Function(
            self, "send-task-lambda-function",
            description="Function to send task to queue",
            code=_lambda.Code.from_asset(os.path.join(os.curdir, "lambda", "send_task")),
            environment={"QUEUE_URL": queue.queue_url},
            handler="index.handler",
            runtime=_lambda.Runtime.PYTHON_3_10,
            layers=[layer],
            log_retention=logs.RetentionDays.ONE_WEEK,
            role=role_lambda_sendtask,
            timeout=Duration.seconds(15),
            # tracing=_lambda.Tracing.ACTIVE,  # X-Ray Tracing
            )
        
        # Lambda function for reading task from queue
        self.lambda_runtask = _lambda.Function(
            self, "run-task-lambda-function",
            description="Function to read task from queue and execute",
            code=_lambda.Code.from_asset(os.path.join(os.curdir, "lambda", "run_task")),
            handler="index.handler",
            runtime=_lambda.Runtime.PYTHON_3_10,
            layers=[layer],
            log_retention=logs.RetentionDays.ONE_WEEK,
            role=role_lambda_runtask,
            timeout=Duration.seconds(15),
            # tracing=_lambda.Tracing.ACTIVE,  # X-Ray Tracing
            )

        # Add SQS as event source
        event_source_queue = SqsEventSource(queue)
        self.lambda_runtask.add_event_source(event_source_queue)

        CfnOutput(self, "SendTaskLambdaServiceRoleName", value=role_lambda_sendtask.role_name,)
        CfnOutput(self, "SendTaskLambdaServiceRoleARN", value=role_lambda_sendtask.role_arn,)
        CfnOutput(self, "RunTaskLambdaServiceRoleName", value=role_lambda_runtask.role_name,)
        CfnOutput(self, "RunTaskLambdaServiceRoleARN", value=role_lambda_runtask.role_arn,)
        CfnOutput(self, "SendTaskFunctionARN", value=self.lambda_sendtask.function_arn,)
        CfnOutput(self, "SendTaskFunctionName", value=self.lambda_sendtask.function_name,)
        CfnOutput(self, "RunTaskFunctionARN", value=self.lambda_runtask.function_arn,)
        CfnOutput(self, "RunTaskFunctionName", value=self.lambda_runtask.function_name,)
