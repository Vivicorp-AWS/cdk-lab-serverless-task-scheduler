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
        # [NOTE] At this time (May 2023, version 2.79.1),
        # CDK doesn't have a L2 EvventBridge Scheduler construct now
        # (Ref: https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_scheduler/README.html)
        # We have to create the Role and Policies by ourselves
        role_scheduler_lambda = iam.Role(self, "InvokeLambdaSchedulerServiceRole",
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

        role_scheduler_lambda.attach_inline_policy(policy_invoke_lambda)

        # EventBridge Scheduler to invoke send-task-lambda-function
        scheduler_lambda = scheduler.CfnSchedule(
            self, "task-scheduler",
            description="Scheduler to invoke send-task-lambda-function",
            # group_name=None,  # [TODO] Has a bug now, add this feature later
            flexible_time_window=scheduler.CfnSchedule.FlexibleTimeWindowProperty(mode="OFF",),
            schedule_expression="at(2037-12-31T23:59:59)",
            schedule_expression_timezone="Asia/Taipei",
            target=scheduler.CfnSchedule.TargetProperty(
                arn=lambdafn.function_arn,
                role_arn=role_scheduler_lambda.role_arn,
                input=json.dumps({}),
                retry_policy=None,
            ),
        )

        CfnOutput(self, "SchedulerRoleName", value=role_scheduler_lambda.role_name,)
        CfnOutput(self, "SchedulerRoleARN", value=role_scheduler_lambda.role_arn,)
        # CfnOutput(self, "SchedulerName", value=scheduler_lambda.name,)  # Causes error for unknown reason
        CfnOutput(self, "SchedulerARN", value=scheduler_lambda.attr_arn,)