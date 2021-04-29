import boto3

from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet


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
        if self._source_data is None:
            iam = boto3.client("iam")
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
        self.copy_if_exists("RoleName", source_data)
        self.copy_if_exists("Description", source_data)
        self.copy_if_exists("AssumeRolePolicyDocument", source_data)
        self.copy_if_exists("MaxSessionDuration", source_data)
        self.copy_if_exists("Path", source_data)

        if "Tags" in source_data:
            self._tags.from_api_result(source_data["Tags"])

        self.is_valid = True

    def derive_path(self):
        start = self._arn.rfind(":") + 1
        fin = self._arn.rfind("/")
        return self._arn[start:fin]

    @property
    def reference(self):
        return self.make_reference(logical_id=self.make_getatt("Arn"))