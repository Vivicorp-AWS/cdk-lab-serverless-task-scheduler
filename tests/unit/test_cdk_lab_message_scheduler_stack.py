import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_lab_message_scheduler.cdk_lab_message_scheduler_stack import CdkLabMessageSchedulerStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_lab_message_scheduler/cdk_lab_message_scheduler_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkLabMessageSchedulerStack(app, "cdk-lab-message-scheduler")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
