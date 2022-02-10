import aws_cdk as core
import aws_cdk.assertions as assertions

from codepipeline_v2.codepipeline_v2_stack import CodepipelineV2Stack

# example tests. To run these tests, uncomment this file along with the example
# resource in codepipeline_v2/codepipeline_v2_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CodepipelineV2Stack(app, "codepipeline-v2")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
