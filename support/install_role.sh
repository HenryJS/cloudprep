#!/usr/bin/env bash

cd "$(dirname $0)" || exit

CloudUser=$1
if [ -z "$CloudUser" ]
then
  echo "Usage: $0 <username>"
fi

sed -E 's/\{User\}/'"$CloudUser"'/'  aws_role.json > aws_role_transformed.json

aws cloudformation deploy --stack-name role-cloudprep --template-file aws_role_transformed.json --capabilities CAPABILITY_IAM
exit $?