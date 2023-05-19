from aws_cdk import (
    Stack,
    aws_sqs as sqs,
    Duration,
    CfnOutput,
)
from constructs import Construct

class SQSStack(Stack):
    def __init__(
            self,
            scope: Construct,
            id: str,
            **kwargs,) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a SQS Queue to store the tasks
        self.queue = sqs.Queue(
            self, "task-queue",
            fifo=True,
            content_based_deduplication=True,
            deduplication_scope=sqs.DeduplicationScope.QUEUE,
            visibility_timeout=Duration.minutes(1),  # How long does a Lambda function process the task
            retention_period=Duration.minutes(15),  # How long does the task remain in the queue
            receive_message_wait_time=Duration.minutes(0),  # How long does the "ReceiveMessage" (Polling) action takes 
        )

        CfnOutput(self, "QueueName", value=self.queue.queue_name,)
        CfnOutput(self, "QueueArn", value=self.queue.queue_arn,)
