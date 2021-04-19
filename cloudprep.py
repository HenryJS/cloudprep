#!/usr/bin/env python3

from cloudprep.aws.AwsInterrogator import AwsInterrogator
from cloudprep.aws.CfnRenderer import CfnRenderer

interrogator = AwsInterrogator()
environment = interrogator.interrogate()
renderer = CfnRenderer(environment)
renderer.render()
