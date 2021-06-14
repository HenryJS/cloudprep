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
    '--bucket',
    action='store',
    dest="bucket",
    const=True,
    default=False,
    nargs="?",
    help='Interrogate Bucket(s)')
parser.add_argument(
    '--kms-key',
    action='store',
    dest="kms_key",
    const=True,
    default=False,
    nargs="?",
    help='Interrogate KMS Key(s)')
parser.add_argument(
    '--kms-alias',
    action='store',
    dest="kms_alias",
    const=True,
    default=False,
    nargs="?",
    help='Interrogate KMS Alias')

options = parser.parse_args()

interrogator = AwsInterrogator()
if options.vpc:
    interrogator.start_vpc(options.vpc)

if options.llambda:
    interrogator.start_lambda(options.llambda)

if options.role:
    interrogator.start_role(options.role)

if options.bucket:
    interrogator.start_bucket(options.bucket)

if options.kms_key:
    interrogator.start_kms_key(options.kms_key)

if options.kms_alias:
    interrogator.start_kms_alias(options.kms_alias)

environment = interrogator.interrogate()
renderer = CfnRenderer(environment)
renderer.render()

if environment._warnings:
    print("Warnings:", file=sys.stderr)
    for warning in environment._warnings:
        print(warning, file=sys.stderr)