from aws_cdk import (
    Stack,
    aws_iam as iam,
    CfnOutput,
)
from constructs import Construct

# [TODO] Add description
class IAMStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Service role for send-message-lambda-function
        self.role_lambda_sendmessage = iam.Role(self, "SendMessageLambdaServiceRole",
            description="Service role for send-message-lambda-function",
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
        policy_manage_sqs = iam.Policy(
            self, "ManageSQSPolicy",
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "sqs:ReceiveMessage",
                        "sqs:DeleteMessage",
                        "sqs:GetQueueAttributes",
                    ],
                    resources=["*"]  # [TODO] Inject SQS Queue
                ),
            ],
        )

        self.role_lambda_sendmessage.attach_inline_policy(policy_manage_logs)
        self.role_lambda_sendmessage.attach_inline_policy(policy_manage_sqs)
