import aws_cdk as core
import aws_cdk.assertions as assertions

from ecs_v2.ecs_v2_stack import EcsV2Stack

# example tests. To run these tests, uncomment this file along with the example
# resource in ecs_v2/ecs_v2_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = EcsV2Stack(app, "ecs-v2")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
