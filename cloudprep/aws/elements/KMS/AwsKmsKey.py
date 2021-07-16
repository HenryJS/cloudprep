import sys

import boto3
from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet


class AwsKmsKey(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::KMS::Key", physical_id, **kwargs)
        if "KmsAlias" in kwargs:
            self._kms_alias = kwargs["KmsAlias"]
        else:
            self._kms_alias = None
        if "KmsAliasCreator" in kwargs:
            self._kms_alias_creator = kwargs["KmsAliasCreator"]
        else:
            self._kms_alias_creator = None

        self.set_defaults({
            "Enabled": True,
            "KeySpec": "SYMMETRIC_DEFAULT",
            "KeyUsage": "ENCRYPT_DECRYPT"
        })
        self._tags = TagSet({"CreatedBy": "CloudPrep"})

    @AwsElement.capture_method
    def capture(self):
        kms = boto3.client("kms")

        if self._source_data is None:
            source_data = kms.describe_key(KeyId=self.physical_id)["KeyMetadata"]
        else:
            source_data = self._source_data
            self._source_data = None

        self.copy_if_exists("Description", source_data)
        self.copy_if_exists("Enabled", source_data)
        self.copy_if_exists("KeyUsage", source_data)
        self._element["EnableKeyRotation"] = kms.get_key_rotation_status(KeyId=self.physical_id)["KeyRotationEnabled"]
        self._element["KeySpec"] = source_data["CustomerMasterKeySpec"]

        self._environment.add_warning("Default Key Policy will be ascribed with single admin and user.", self.physical_id)
        self._element["KeyPolicy"] = self.default_kms_policy()
        self._environment.add_parameter(
            Name="KmsKeyAdministrator",
            Description="The ARN of the administrator for your KMS keys."
        )

        self._element["PendingWindowInDays"] = 30
        self._environment.add_warning("Setting termination to 30 for key deleted using CFN.", self.physical_id)

        self._tags.from_api_result(kms.list_resource_tags(KeyId=self.physical_id)["Tags"])

        if self._kms_alias is None:
            self.check_for_aliases(kms)

        self.is_valid = True

    def check_for_aliases(self, kms):
        for page in  kms.get_paginator('list_aliases').paginate():
            for alias in page["Aliases"]:
                if "TargetKeyId" in alias and alias["TargetKeyId"] == self.physical_id:
                    self._environment.add_to_todo(self._kms_alias_creator(self._environment, alias["AliasName"]))

    def default_kms_policy(self):
        return {
          'Version': '2012-10-17',
          'Id': 'key-consolepolicy-3',
          'Statement': [
            {
              'Sid': 'Enable IAM User Permissions',
              'Effect': 'Allow',
              'Principal': {
                'AWS': { "Fn::Sub": 'arn:aws:iam::${AWS::AccountId}:root'}
              },
              'Action': 'kms:*',
              'Resource': '*'
            },
            {
              'Sid': 'Allow access for Key Administrators',
              'Effect': 'Allow',
              'Principal': {
                'AWS': { "Ref": "KmsKeyAdministrator" }
              },
              'Action': [
                'kms:Create*',
                'kms:Describe*',
                'kms:Enable*',
                'kms:List*',
                'kms:Put*',
                'kms:Update*',
                'kms:Revoke*',
                'kms:Disable*',
                'kms:Get*',
                'kms:Delete*',
                'kms:TagResource',
                'kms:UntagResource',
                'kms:ScheduleKeyDeletion',
                'kms:CancelKeyDeletion'
              ],
              'Resource': '*'
            },
            {
              'Sid': 'Allow use of the key',
              'Effect': 'Allow',
              'Principal': {
                'AWS': { "Ref": "KmsKeyAdministrator" }
              },
              'Action': [
                'kms:Encrypt',
                'kms:Decrypt',
                'kms:ReEncrypt*',
                'kms:GenerateDataKey*',
                'kms:DescribeKey'
              ],
              'Resource': '*'
            },
            {
              'Sid': 'Allow attachment of persistent resources',
              'Effect': 'Allow',
              'Principal': {
                'AWS': { "Ref": "KmsKeyAdministrator" }
              },
              'Action': [
                'kms:CreateGrant',
                'kms:ListGrants',
                'kms:RevokeGrant'
              ],
              'Resource': '*',
              'Condition': {
                'Bool': {
                  'kms:GrantIsForAWSResource': 'true'
                }
              }
            }
          ]
        }