#!/usr/bin/env python3

import json
from cloudprep.aws.elements.S3.AwsBucketPolicy import AwsBucketPolicy


class env:
    # swallow undefined methods
    def __getattr__(self, item):
        def method(*args):
            pass

        return method


policy_content = json.dumps({
    "Version": "2012-10-17",
    "Id": "S3-Console-Auto-Gen-Policy-1620678499815",
    "Statement": [{
        "Sid": "S3PolicyStmt-DO-NOT-MODIFY-1620678499421",
        "Effect": "Allow",
        "Principal": {"Service": "s3.amazonaws.com"},
        "Action": "s3:PutObject",
        "Resource": "arn:aws:s3:::hjs-test/*",
        "Condition": {
            "StringEquals": {
                "aws:SourceAccount": "368255555983",
                "s3:x-amz-acl": "bucket-owner-full-control"
            },
            "ArnLike": {
                "aws:SourceArn": "arn:aws:s3:::hjs-test"
            }
        }
    }]
})

dummy_env = env()
bucket = AwsBucketPolicy(
    dummy_env,
    original_bucket="hjs-test",
    bucket_name="arn:aws:s3:::${AWS::StackName}-${AWS::AccountId}-${AWS::Region}-hjs-test",
    policy_data=policy_content
)

bucket.capture()
print(json.dumps(bucket._element["PolicyDocument"], indent=2))
