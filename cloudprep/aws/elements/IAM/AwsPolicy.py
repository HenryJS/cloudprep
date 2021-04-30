import boto3
import sys

from ..AwsElement import AwsElement
from ..TagSet import TagSet
from ..AwsARN import AwsARN


class AwsPolicy(AwsElement):
    def __init__(self, environment, arn, **kwargs):
        super().__init__(environment, "AWS::IAM::Policy", arn.resource_id, **kwargs)

        self._arn = arn

        self._dependents = {
            "Groups": [],
            "Roles": [],
            "Users": []
        }

        self.set_defaults({
        })

    @AwsElement.capture_method
    def capture(self):
        iam = boto3.client("iam")
        this_policy = iam.get_policy(PolicyArn=self._arn.text)["Policy"]
        this_version = iam.get_policy_version(
            PolicyArn=self._arn.text,
            VersionId=this_policy["DefaultVersionId"]
        )
        # TODO: The Resource section will have a load of values that will not apply in the new world!
        self._element["PolicyDocument"] = this_version["PolicyVersion"]["Document"]

        self.is_valid = True
        return

    def add_dependant_role(self, role):
        self._dependents["Roles"].append(role)

    def add_dependant_user(self, user):
        self._dependents["Users"].append(user)

    def add_dependant_group(self, user):
        self._dependents["Groups"].append(user)

    @AwsElement.finalise_method
    def finalise(self):
        for dep_type in ["Groups", "Roles", "Users"]:
            if self._dependents[dep_type]:
                self._element[dep_type] = []
                for dependent in self._dependents[dep_type]:
                    self._element[dep_type].append(dependent.reference)
