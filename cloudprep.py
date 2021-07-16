#!/usr/bin/env python3

import argparse
import sys

from cloudprep.aws.AwsInterrogator import AwsInterrogator
from cloudprep.aws.CfnRenderer import CfnRenderer

parser = argparse.ArgumentParser(description='Record AWS configuration.')
parser.add_argument(
    '--vpc',
    action='store',
    dest="vpc",
    const=True,
    default=False,
    nargs="?",
    help='Interrogate VPCs')
parser.add_argument(
    '--llambda',
    action='store',
    dest="llambda",
    const=True,
    default=False,
    nargs="?",
    help='Interrogate Lambdas')
parser.add_argument(
    '--role',
    action='store',
    dest="role",
    help='Interrogate Lambdas')
parser.add_argument(
    '--stepfn',
    action='store',
    dest="stepfn",
    const=True,
    default=False,
    nargs="?",
    help='Interrogate Step Function(s)')
options = parser.parse_args()

interrogator = AwsInterrogator()
if options.vpc:
    interrogator.start_vpc(options.vpc)

if options.llambda:
    interrogator.start_lambda(options.llambda)

if options.role:
    interrogator.start_role(options.role)

if options.stepfn:
    interrogator.start_stepfn(options.stepfn)

environment = interrogator.interrogate()
renderer = CfnRenderer(environment)
renderer.render()
