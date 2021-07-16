from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet

import boto3


class AwsLogGroup(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::Logs::LogGroup", physical_id, **kwargs)
        self.set_defaults({})

    @AwsElement.capture_method
    def capture(self):
        logs = boto3.client("logs")

        source_data = None
        matches = logs.describe_log_groups(logGroupNamePrefix=self.physical_id)["logGroups"]
        for match in matches:
            if match["logGroupName"] == self.physical_id:
                source_data = match
        if source_data is None:
            raise Exception("Couldn't find LogGroup matching " + self.physical_id)

        self._element["RetentionInDays"] = source_data["retentionInDays"]
        #  TODO:       "KmsKeyId": String,

        self.is_valid = True
