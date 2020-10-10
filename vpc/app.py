#!/usr/bin/env python3

from aws_cdk import core
from vpc.vpc_stack import VpcStack
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
VpcStack(app, "vpc", env=env)
app.synth()
