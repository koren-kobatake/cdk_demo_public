import aws_cdk as core
import aws_cdk.assertions as assertions

from vpc_v2.vpc_v2_stack import VpcV2Stack

# example tests. To run these tests, uncomment this file along with the example
# resource in vpc_v2/vpc_v2_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = VpcV2Stack(app, "vpc-v2")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
