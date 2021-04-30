import boto3
import sys

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


        # {
        #   "Type" : "AWS::IAM::Role",
        #   "Properties" : {
        #       "ManagedPolicyArns" : [ String, ... ],
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
                    print("Need to make a Role!", file=sys.stderr)

        if managed_arns:
            self._element["ManagedPolicyArns"] = managed_arns

        self.is_valid = True

    def derive_path(self):
        start = self._arn.rfind(":") + 1
        fin = self._arn.rfind("/")
        return self._arn[start:fin]

    @property
    def reference(self):
        return self.make_reference(logical_id=self.make_getatt("Arn"))