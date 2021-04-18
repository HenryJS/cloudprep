#!/usr/bin/env python3

from cloudprep.aws import AwsInterrogator, CfnRenderer

interrogator = AwsInterrogator.AwsInterrogator()
renderer = CfnRenderer.CfnRenderer()


environment = interrogator.interrogate()
renderer.render(environment)

