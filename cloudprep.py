#!/usr/bin/env python3

from cloudprep.aws.AwsInterrogator import AwsInterrogator
from cloudprep.aws.CfnRenderer import CfnRenderer


environment = AwsInterrogator.interrogate()
renderer = CfnRenderer(environment)
renderer.render()
