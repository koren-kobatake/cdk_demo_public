#!/usr/bin/env python3

from aws_cdk import core
from alb.alb_stack import AlbStack
import os

ACCOUNT_ID = os.environ.get('ACCOUNT_ID')
REGION = os.environ.get('REGION')
if not ACCOUNT_ID:
    raise Exception('[error] ACCOUNT_ID')
if not REGION:
    raise Exception('[error] REGION')
env = {
    'region':REGION,
    'account':ACCOUNT_ID,
}
app = core.App()
AlbStack(app, "alb", env=env)
app.synth()
