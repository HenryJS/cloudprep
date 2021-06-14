import json
import boto3
import sys
from ..AwsARN import AwsARN
from cloudprep.aws.elements.AwsElement import AwsElement

class AwsBucketPolicy(AwsElement):
    def __init__(self, environment, **kwargs):
        super().__init__(environment, "AWS::S3::BucketPolicy", kwargs["original_bucket"] + "-policy", **kwargs)
        self._policy_doc = kwargs["policy_data"]
        self._original_bucket = kwargs["original_bucket"]
        self._bucket = kwargs["bucket"]


    @AwsElement.capture_method
    def capture(self):
        self._element["Bucket"] = self._bucket.make_reference()
        account_id = boto3.client('sts').get_caller_identity().get('Account')

        policy_json = json.loads(self._policy_doc)
        for stmt in policy_json["Statement"]:
            stmt["Resource"] = {
                "Fn::Join": ["", [ self._bucket.make_getatt("Arn"), "/*" ] ]
            }

            # There may be conditions attached.
            if "Condition" in stmt:
                for comparitor, clause in stmt["Condition"].items():
                    if "aws:SourceAccount" in clause and clause["aws:SourceAccount"] == account_id:
                        clause ["aws:SourceAccount"] = {"Fn::Sub": "${AWS::AccountId}"}
                        self._environment.add_warning("aws:SourceAccount assumed to be my account in AwsBucketPolicy", self.physical_id)

                    if "aws:SourceArn" in clause:
                        source_arn = AwsARN(stmt["Condition"]["ArnLike"]["aws:SourceArn"])
                        if source_arn.resource_id == self._original_bucket:
                            clause["aws:SourceArn"] = self._bucket.make_getatt("Arn")

        self._element["PolicyDocument"] = policy_json
        self.is_valid = True
