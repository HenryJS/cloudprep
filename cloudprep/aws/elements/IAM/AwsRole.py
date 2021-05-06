import boto3
import sys

from .AwsPolicy import AwsPolicy
from .AwsManagedPolicy import AwsManagedPolicy
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
        #       "PermissionsBoundary" : String,


        # Copying RoleName will cause conflicts, so let's not do it.
        self.copy_if_exists("Description", source_data)
        self.copy_if_exists("AssumeRolePolicyDocument", source_data)
        self.copy_if_exists("MaxSessionDuration", source_data)
        self.copy_if_exists("Path", source_data)

        if "Tags" in source_data:
            self._tags.from_api_result(source_data["Tags"])

        # Deal with Managed Policies
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
                    pol = AwsManagedPolicy(self._environment, policy_arn)
                    managed_arns.append(pol.reference)
                    self._environment.add_to_todo(pol)

        if managed_arns:
            self._element["ManagedPolicyArns"] = managed_arns

        # Inline Policies
        inline_policies = []
        inline_policy_pages = iam.get_paginator("list_role_policies").paginate(RoleName=self.physical_id)
        for page in inline_policy_pages:
            for policy_name in page["PolicyNames"]:
                inline_policy = iam.get_role_policy(RoleName=self.physical_id, PolicyName=policy_name)
                del inline_policy["RoleName"]
                del inline_policy["ResponseMetadata"]
                inline_policies.append(inline_policy)

        if inline_policies:
            self._element["Policies"] = inline_policies

        # Permissions Boundary
        if "PermissionsBoundary" in source_data:
            if source_data["PermissionsBoundary"]["PermissionsBoundaryType"] == "Policy":
                policy_arn = AwsARN(source_data["PermissionsBoundary"]["PermissionsBoundaryArn"])
                # is it managed?
                if policy_arn.account == "aws":
                    self._element["PermissionsBoundary"] = policy_arn.text
                else:
                    pol = AwsManagedPolicy(self._environment, policy_arn)
                    self._element["PermissionsBoundary"] =pol.reference
                    self._environment.add_to_todo(pol)

        self.is_valid = True

    def policy_from_arn(self, policy_arn):
        pass

    def derive_path(self):
        start = self._arn.rfind(":") + 1
        fin = self._arn.rfind("/")
        return self._arn[start:fin]

