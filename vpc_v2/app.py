#!/usr/bin/env python3
import os

import aws_cdk as cdk

from vpc_v2.vpc_v2_stack import VpcV2Stack


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
env=cdk.Environment(account=ACCOUNT_ID, region=REGION)

app = cdk.App()
VpcV2Stack(app, "VpcV2Stack", env=env)

app.synth()
