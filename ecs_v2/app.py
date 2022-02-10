#!/usr/bin/env python3
import os

import aws_cdk as cdk

from ecs_v2.ecs_v2_stack import EcsV2Stack

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
EcsV2Stack(app, "EcsV2Stack", env=env)

app.synth()
