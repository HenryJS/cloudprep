#!/usr/bin/env python3

import argparse
import sys

from cloudprep.aws.AwsInterrogator import AwsInterrogator
from cloudprep.aws.CfnRenderer import CfnRenderer

parser = argparse.ArgumentParser(description='Record AWS configuration.')
parser.add_argument(
    '--vpc',
    action='store_true',
    help='Interrogate VPCs')
parser.add_argument(
    '--llambda',
    action='store',
    dest="llambda",
    const=True,
    default=False,
    nargs="?",
    help='Interrogate Lambdas')
options = parser.parse_args()

interrogator = AwsInterrogator()
if options.vpc:
    interrogator.start_vpc()

if options.llambda:
    interrogator.start_lambda(options.llambda)

environment = interrogator.interrogate()
renderer = CfnRenderer(environment)
renderer.render()
