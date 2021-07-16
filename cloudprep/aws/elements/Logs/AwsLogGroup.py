from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet

import boto3


class AwsLogGroup(AwsElement):
    def __init__(self, environment, arn, **kwargs):
        self._arn = arn
        super().__init__(environment, "AWS::Logs::LogGroup", arn.resource_id, **kwargs)
        self.set_defaults({})

    @AwsElement.capture_method
    def capture(self):
        logs = boto3.client("logs")

        source_data = None
        prefix = "{}/{}".format(self._arn.resource_path, self._arn.resource_id)
        matches = logs.describe_log_groups(logGroupNamePrefix=prefix)["logGroups"]
        for match in matches:
            if match["logGroupName"] == prefix:
                source_data = match
        if source_data is None:
            raise Exception("Couldn't find LogGroup matching " + prefix)

        self._element["RetentionInDays"] = source_data["retentionInDays"]
        #  TODO:       "KmsKeyId": String,

        self.is_valid = True
