#!/usr/bin/env python3

from aws_cdk import core
from ecs.ecs_stack import EcsStack
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

app = core.App()
EcsStack(app, "ecs", env=env)

app.synth()
