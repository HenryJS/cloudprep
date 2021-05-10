import boto3
import botocore.exceptions
import sys
from .AwsBucketPolicy import AwsBucketPolicy
from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet


class AwsBucket(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::S3::Bucket", physical_id, **kwargs)
        self.set_defaults({
            "AccessControl": "Private",
            "PublicAccessBlockConfiguration": {
                    "BlockPublicAcls": False,
                    "BlockPublicPolicy": False,
                    "IgnorePublicAcls": False,
                    "RestrictPublicBuckets": False
            }
        })
        self._tags = TagSet({"CreatedBy": "CloudPrep"})
        self._bucket_filter = { "Bucket": self.physical_id }


    @AwsElement.capture_method
    def capture(self):
        s3 = boto3.client("s3")
        # {
        #  TODO:     "AccessControl" : String,
        #  TODO:     "AnalyticsConfigurations" : [ AnalyticsConfiguration, ... ],
        #  TODO:     "CorsConfiguration" : CorsConfiguration,
        #  TODO:     "IntelligentTieringConfigurations" : [ IntelligentTieringConfiguration, ... ],
        #  TODO:     "InventoryConfigurations" : [ InventoryConfiguration, ... ],
        #  TODO:     "LifecycleConfiguration" : LifecycleConfiguration,
        #  TODO:     "LoggingConfiguration" : LoggingConfiguration,
        #  TODO:     "MetricsConfigurations" : [ MetricsConfiguration, ... ],
        #  TODO:     "NotificationConfiguration" : NotificationConfiguration,
        #  TODO:     "OwnershipControls" : OwnershipControls,
        #  TODO:     "ReplicationConfiguration" : ReplicationConfiguration,
        #  TODO:     "VersioningConfiguration" : VersioningConfiguration,
        #  TODO:     "WebsiteConfiguration" : WebsiteConfiguration
        # }

        # The AWS S3 API is clunkier than their newer offerings.  Each property requires a separate call; if that
        # property is not present on the bucket then, rather than returning None (or similar), an exception is thrown.
        # We don't particularly care about the exceptions so we just *pass* onto the next element.

        # Acceleration
        accc = self.wrap_call(s3.get_bucket_accelerate_configuration)
        if accc and "Status" in accc:
            self._element["AccelerateConfiguration"] = {
                "AccelerationStatus": accc["Status"]
            }

        # Bucket Z
        # TODO: KMS Keys
        bz = self.wrap_call(s3.get_bucket_encryption)
        if bz:
            for rule in bz["ServerSideEncryptionConfiguration"]["Rules"]:
                rule["ServerSideEncryptionByDefault"] = rule["ApplyServerSideEncryptionByDefault"]
                del rule["ApplyServerSideEncryptionByDefault"]
            self._element["BucketEncryption"] = {
                "ServerSideEncryptionConfiguration": bz["ServerSideEncryptionConfiguration"]["Rules"]
            }

        # Object Lock Configuration
        olc = self.wrap_call(s3.get_object_lock_configuration)
        if olc and olc["ObjectLockConfiguration"]["ObjectLockEnabled"] == "Enabled":
                self._element["ObjectLockEnabled"] = True
                self._element["ObjectLockConfiguration"] = olc["ObjectLockConfiguration"]

        # Public Acces Block configuration
        pabc = self.wrap_call(s3.get_public_access_block)
        if pabc:
            self._element["PublicAccessBlockConfiguration"] = pabc["PublicAccessBlockConfiguration"]

        # Tags
        tagging = self.wrap_call(s3.get_bucket_tagging)
        if tagging:
            self._tags.from_api_result(tagging["TagSet"])

        # Do we have a policy?
        bucket_policy = self.wrap_call(s3.get_bucket_policy)
        if bucket_policy:
            self._environment.add_to_todo(
                AwsBucketPolicy(self._environment, bucket_name=self.physical_id, policy_data=bucket_policy["Policy"])
            )

        self.is_valid = True

    def wrap_call(self, call):
        try:
            result = call(**(self._bucket_filter))
        except Exception as e:
            return None
        return result
