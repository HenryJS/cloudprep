#!/usr/bin/env bash

aws cloudformation deploy --stack-name role-cloudprep --template-file support/aws_role.json --capabilities CAPABILITY_IAM
exit $?