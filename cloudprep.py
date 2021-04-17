#!/usr/bin/env python3

from cloudprep.aws import AwsEnvironment, AwsInterrogator, CfnRenderer
# import cloudprep.aws

interrogator = AwsInterrogator.AwsInterrogator()
renderer = CfnRenderer.CfnRenderer()


environment = interrogator.interrogate()
renderer.render(environment)