#!/usr/bin/env python3
import os

import aws_cdk as cdk

from codepipeline_v2.codepipeline_v2_stack import CodepipelineV2Stack

import os

ACCOUNT_ID = os.environ.get('ACCOUNT_ID')
if not ACCOUNT_ID:
    raise Exception('not set ACCOUNT_ID')
REGION = os.environ.get('REGION')
if not REGION:
    raise Exception('not set REGION')

env = {
    'region':REGION,
    'account':ACCOUNT_ID,
}



app = cdk.App()
CodepipelineV2Stack(app, "CodepipelineV2Stack", env=env)

app.synth()
