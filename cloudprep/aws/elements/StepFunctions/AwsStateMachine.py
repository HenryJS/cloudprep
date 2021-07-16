from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet
from ..AwsARN import AwsARN
from ..IAM.AwsRole import AwsRole
from ..Logs.AwsLogGroup import AwsLogGroup

import boto3
import json
import sys

class AwsStateMachine(AwsElement):
    def __init__(self, environment, arn, **kwargs):
        super().__init__(environment, "AWS::StepFunctions::StateMachine", arn.resource_id, **kwargs)
        self._arn = arn
        self.set_defaults({
            "StateMachineType": "STANDARD",
            "TracingConfiguration": {"Enabled": False},
            "LoggingConfiguration": {
                "Level": "OFF",
                "IncludeExecutionData": False
            }
        })
        self._tags = TagSet({"CreatedBy": "CloudPrep"})

    @AwsElement.capture_method
    def capture(self):
        sfn = boto3.client('stepfunctions')

        if self._source_data is None:
            source_data = sfn.describe_state_machine(stateMachineArn=self._arn.text)
        else:
            source_data = self._source_data
            self._source_data = None

        # TODO: Look for Lambdas and shell out
        self._element["Definition"] = json.loads(source_data["definition"])

        slc = source_data["loggingConfiguration"]
        lc = {"Level": slc["level"]}
        if "includeExecutionData" in slc:
            lc["IncludeExecutionData"] = slc["includeExecutionData"]
        if "destinations" in slc:
            actual_arn = AwsARN(slc["destinations"][0]["cloudWatchLogsLogGroup"]["logGroupArn"])
            log_group = AwsLogGroup(self._environment, actual_arn.resource_id)
            lc["Destinations"] = [{"CloudWatchLogsLogGroup": {"LogGroupArn": log_group.make_getatt("Arn")}}]
        self._element["LoggingConfiguration"] = lc

        # TODO: Ensure the Role grants privileges to the right CloudWatch Logs Group!
        # TODO: Ensure the Role grants privileges to use any applicable Lambdas
        self._element["RoleArn"] = AwsRole(self._environment, AwsARN(source_data["roleArn"])).make_getatt("Arn")
        self._element["StateMachineType"] = source_data["type"]
        self._element["TracingConfiguration"] = {"Enabled": source_data["tracingConfiguration"]["enabled"]}

        self._tags.from_api_result(sfn.list_tags_for_resource(resourceArn=self._arn.text)["tags"])

        self.is_valid = True
