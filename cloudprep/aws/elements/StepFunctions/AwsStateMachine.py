from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet
from ..AwsARN import AwsARN
from ..IAM.AwsRole import AwsRole
from ..Logs.AwsLogGroup import AwsLogGroup
from ..Lambda.AwsLambdaFunction import AwsLambdaFunction

import boto3
import json
import sys

class AwsStateMachine(AwsElement):
    def __init__(self, environment, arn, **kwargs):
        super().__init__(environment, "AWS::StepFunctions::StateMachine", "states-"+arn.resource_id, **kwargs)
        self._arn = arn
        self.set_defaults({
            "StateMachineType": "STANDARD",
            "TracingConfiguration": {"Enabled": False},
            "LoggingConfiguration": {
                "Level": "OFF",
                "IncludeExecutionData": False
            }
        })
        self._tags = TagSet()

    @AwsElement.capture_method
    def capture(self):
        sfn = boto3.client('stepfunctions')

        if self._source_data is None:
            source_data = sfn.describe_state_machine(stateMachineArn=self._arn.text)
        else:
            source_data = self._source_data
            self._source_data = None

        self._element["Definition"] = json.loads(source_data["definition"])
        self.detect_lambdas(self._element["Definition"])

        slc = source_data["loggingConfiguration"]
        lc = {"Level": slc["level"]}
        if "includeExecutionData" in slc:
            lc["IncludeExecutionData"] = slc["includeExecutionData"]
        if "destinations" in slc:
            actual_arn = AwsARN(slc["destinations"][0]["cloudWatchLogsLogGroup"]["logGroupArn"])
            log_group = AwsLogGroup(self._environment, actual_arn)
            lc["Destinations"] = [{"CloudWatchLogsLogGroup": {"LogGroupArn": log_group.make_getatt("Arn")}}]
        self._element["LoggingConfiguration"] = lc

        # TODO: Ensure the Role grants privileges to the right CloudWatch Logs Group!
        # TODO: Ensure the Role grants privileges to use any applicable Lambdas
        self._element["RoleArn"] = AwsRole(self._environment, AwsARN(source_data["roleArn"])).make_getatt("Arn")
        self._element["StateMachineType"] = source_data["type"]
        self._element["TracingConfiguration"] = {"Enabled": source_data["tracingConfiguration"]["enabled"]}

        self._tags.from_api_result(sfn.list_tags_for_resource(resourceArn=self._arn.text)["tags"])

        self.is_valid = True

    def detect_lambdas(self, definition):
        for _, state in definition["States"].items():
            self.lambda_process_state(state)

    def lambda_process_state(self, state):
        if state["Type"] == "Task":
            try:
                arn = AwsARN(state["Resource"])
                if arn.resource_type == "lambda" and arn.resource_id == "invoke":
                    lmb = AwsLambdaFunction(self._environment, state["Parameters"]["FunctionName"])
                    state["Parameters"]["FunctionName"] = lmb.reference
                    self._environment.add_to_todo(lmb)
            except Exception as e:
                # Super bad practice but hey.  It wasn't an ARN.
                pass

            pass

        # Branches can contain other states
        elif state["Type"] == "Parallel":
            for branch in state["Branches"]:
                self.detect_lambdas(branch)

        # Don't care about anything else :)

