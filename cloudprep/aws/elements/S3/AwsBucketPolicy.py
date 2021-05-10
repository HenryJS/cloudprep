import json
import boto3
from ..AwsARN import AwsARN
from cloudprep.aws.elements.AwsElement import AwsElement

class AwsBucketPolicy(AwsElement):
    def __init__(self, environment, **kwargs):
        super().__init__(environment, "AWS::S3::BucketPolicy", kwargs["original_bucket"] + "-policy", **kwargs)
        self._bucket = kwargs["bucket_name"]
        self._policy_doc = kwargs["policy_data"]
        self._original_bucket = kwargs["original_bucket"]


    @AwsElement.capture_method
    def capture(self):
        self._element["Bucket"] = {"Fn::Sub": self._bucket}
        account_id = boto3.client('sts').get_caller_identity().get('Account')

        policy_json = json.loads(self._policy_doc)
        for stmt in policy_json["Statement"]:
            # The ResourceArn probably points to a static bucket.
            resource_arn = AwsARN(stmt["Resource"])
            if resource_arn.resource_type:
                resource_arn.resource_type = self._bucket
            else:
                resource_arn.resource_id = self._bucket
            # self._environment.add_warning("Translating resource "+stmt["Resource"] + " to " + resource_arn.text, self)
            stmt["Resource"] = {"Fn::Sub": resource_arn.text}

            # There may be conditions attached.
            if "Condition" in stmt:
                for comparitor, clause in stmt["Condition"].items():
                    if "aws:SourceAccount" in clause and clause["aws:SourceAccount"] == account_id:
                        clause ["aws:SourceAccount"] = {"Fn::Sub": "${AWS::AccountId}"}
                        self._environment.add_warning("aws:SourceAccount assumed to be my account in AwsBucketPolicy", self.physical_id)

                    if "aws:SourceArn" in clause:
                        source_arn = AwsARN(stmt["Condition"]["ArnLike"]["aws:SourceArn"])
                        if source_arn.resource_id == self._original_bucket:
                            source_arn.resource_id = self._bucket
                            clause ["aws:SourceArn"] = {"Fn::Sub": source_arn.text}

        self._element["PolicyDocument"] = policy_json
        self.is_valid = True
