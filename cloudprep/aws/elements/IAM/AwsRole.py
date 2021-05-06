import boto3
import sys

from .AwsPolicy import AwsPolicy
from ..AwsElement import AwsElement
from ..TagSet import TagSet
from ..AwsARN import AwsARN


class AwsRole(AwsElement):
    def __init__(self, environment, arn, **kwargs):
        super().__init__(environment, "AWS::IAM::Role", arn.resource_id, **kwargs)

        self._arn = arn
        self._tags = TagSet({"CreatedBy": "CloudPrep"})

        self.set_defaults({
            "MaxSessionDuration": 3600,
            "Path": "/"
        })

    @AwsElement.capture_method
    def capture(self):
        iam = boto3.client("iam")
        if self._source_data is None:
            source_data = iam.get_role(RoleName=self.physical_id)["Role"]
        else:
            source_data = self._source_data
            self._source_data = None

        # { TODO: Inline Policies
        #   "Type" : "AWS::IAM::Role",
        #   "Properties" : {
        #       "PermissionsBoundary" : String,
        #       "Policies" : [ Policy, ... ],
        #     }
        # }

        # Copying RoleName will cause conflicts, so let's not do it.
        # self.copy_if_exists("RoleName", source_data)

        self.copy_if_exists("Description", source_data)
        self.copy_if_exists("AssumeRolePolicyDocument", source_data)
        self.copy_if_exists("MaxSessionDuration", source_data)
        self.copy_if_exists("Path", source_data)

        if "Tags" in source_data:
            self._tags.from_api_result(source_data["Tags"])

        # Deal with attached policies!
        attached_policy_pages = iam.get_paginator("list_attached_role_policies")\
            .paginate(RoleName=self.physical_id)

        managed_arns = []
        for page in attached_policy_pages:
            for policy in page["AttachedPolicies"]:
                policy_arn = AwsARN(policy["PolicyArn"])
                # is it managed?
                if policy_arn.account == "aws":
                    managed_arns.append(policy["PolicyArn"])

                else:
                    pol = AwsPolicy(self._environment, policy_arn)
                    pol.add_dependant_role(self)
                    self._environment.add_to_todo(pol)

        if managed_arns:
            self._element["ManagedPolicyArns"] = managed_arns

        self.is_valid = True

    def policy_from_arn(self, policy_arn):
        pass

    def derive_path(self):
        start = self._arn.rfind(":") + 1
        fin = self._arn.rfind("/")
        return self._arn[start:fin]

