from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_scheduler as scheduler,
    CfnOutput,
)
from constructs import Construct
import json

class SchedulerStack(Stack):
    def __init__(
            self,
            scope: Construct,
            id: str,
            lambdafn,
            **kwargs,) -> None:
        super().__init__(scope, id, **kwargs)

        # Service role for task-scheduler
        role_scheduler = iam.Role(self, "InvokeLambdaSchedulerServiceRole",
            description="Service role for task-scheduler",
            assumed_by=iam.ServicePrincipal("scheduler.amazonaws.com"),
        )

        # Policy for invoking Lambda Function
        policy_invoke_lambda = iam.Policy(
            self, "InvokeLambdaFunctionPolicy",
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "lambda:InvokeFunction",
                    ],
                    resources=[
                        lambdafn.function_arn,
                        f"{lambdafn.function_arn}:*",
                    ]
                ),
            ],
        )

        role_scheduler.attach_inline_policy(policy_invoke_lambda)

        # EventBridge Scheduler to invoke send-task-lambda-function
        scheduler.CfnSchedule(
            self, "task-scheduler",
            description="Scheduler to invoke send-task-lambda-function",
            flexible_time_window=scheduler.CfnSchedule.FlexibleTimeWindowProperty(mode="OFF",),
            schedule_expression="at(2037-12-31T23:59:59)",
            schedule_expression_timezone="Asia/Taipei",
            target=scheduler.CfnSchedule.TargetProperty(
                arn=lambdafn.function_arn,
                role_arn=role_scheduler.role_arn,
                input=json.dumps({}),
            ),
            retry_policy=None,
        )