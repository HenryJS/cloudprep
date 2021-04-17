#!/usr/bin/env python3

from cloudprep.aws import AwsEnvironment, AwsInterrogator, CfnRenderer
import cloudprep.aws

environment = AwsEnvironment.AwsEnvironment()
interrogator = AwsInterrogator.AwsInterrogator()
renderer = CfnRenderer.CfnRenderer()


interrogator.interrogate(environment)
renderer.render(environment)