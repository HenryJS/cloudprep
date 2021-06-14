import boto3
from .AwsKmsKey import AwsKmsKey
from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet


class AwsKmsAlias(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        if not physical_id.startswith("alias/"):
            physical_id = "alias/" + physical_id

        super().__init__(environment, "AWS::KMS::Alias", physical_id, **kwargs)
        self.set_defaults({})

    @AwsElement.capture_method
    def capture(self):
        kms = boto3.client("kms")

        paginator = kms.get_paginator('list_aliases')
        found = False
        for page in paginator.paginate():
            for alias in page["Aliases"]:
                if alias["AliasName"] == self.physical_id:
                    source_data = alias
                    found=True
        if not found:
            raise Exception("Cannot find alias " + self.physical_id)

        self._element["AliasName"] = {"Fn::Sub": "alias/" + self.make_unique(source_data["AliasName"][6:])}

        key = AwsKmsKey(self._environment, source_data["TargetKeyId"])
        self._environment.add_to_todo(key)
        self._element["TargetKeyId"] = key.make_getatt("Arn")

        self.is_valid = True
