# CDK Lab - Serverless Task Scheduler

I used to schedule some cron tasks and send the results to IM application, such as Slack, Discord ...etc.

What I did before was implementing a gigantic, stable, famous workflow platform like [Apache Airflow](https://airflow.apache.org) and [Prefect](https://www.prefect.io). They are still good choices, but it's time for me to adopt a lighter, event-driven architecture.

When talk about AWS, we can use Amazon EventBridge, AWS Lambda, Amazon SQS to build the same architecture to fulfill the same job:

![](./diagram-services.jpg)

Hope this will cost less money and effort. Let's get hands dirty 🛠️ and make the party started! 🎉

## Components

![](diagram-detailed.jpg)

All we need are:

* **EventBridge Scheduler (Event Scheduler)**: Schedule to invoke a Lambda function with a Role attached
  * **Service Role**: Has permission to
    * Invoke a Lambda function (`lambda:InvokeFunction`)
* **Lambda function (Send Tasks)**: Send messages to queue with a Role attached
  * **Service Role**: Has permission to
    * Send messages to SQS (`sqs:SendMessage`)
    * Manage CloudWatch logs (`logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`)
* **Queue**: Store the tasks
* **Lambda function (Run Task)**: Receive messages from queue with a Role attached
  * **Service Role**: Has permission to
      * Receive message from queue (`sqs:ReceiveMessage`, `sqs:DeleteMessage`, `sqs:GetQueueAttributes`)
      * Manage CloudWatch logs (`logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`)

The creation order might be:

1. Create Lambda functions with roles
2. Create queue
3. Grant SQS permissions to Lambda's roles
   1. `aws_cdk.aws_sqs.Queue.grant_send_messages()`
   2. `aws_cdk.aws_sqs.Queue.grant_consume_messages()`
4. ([NOTE]) Create a role for scheduler, with `lambda:InvokeFunction` permission
5. ([NOTE]) Create a scheduler, attach a Role, set a Lambda target

> [NOTE] According to the [document](https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_scheduler/README.html): Currently (May 2023) there is still no L2 construct yet, so the scheduler object doesn't have a method like `grant_a_permission()` to use.
>
> If L2 construct is available in the future, change the order as below:

1. Create Lambda functions with roles
2. Create queue
3. Grant SQS permissions to Lambda's roles
   1. `aws_cdk.aws_sqs.Queue.grant_send_messages()`
   2. `aws_cdk.aws_sqs.Queue.grant_consume_messages()`
4. Create a scheduler, set a Lambda target
5. Grant Lambda permission to scheduler role
   1. `aws_cdk.aws_lambda.Function.grant_invoke()`

## Instructions

### Install Python Lambda Layer (Python dependencies)

All Python dependencies must stored under `layer/python` as [Lambda Layer](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html) then pack and send to AWS Lambda.

If the CDK process is executed with your own instance, install the dependencies with the command below: 

```bash
pip install --target ./layer/python <package>
```

Remember to manually add dependencies to `requirements-layer.txt`, so we can add a step to install the layers by executing `pip install -r requirements-layer.txt ./layer/python` when we run CI/CD.
