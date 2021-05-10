import boto3
import botocore.exceptions
import sys
from ..AwsARN import AwsARN
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
        #  TODO:     "CorsConfiguration" : CorsConfiguration,
        #  TODO:     "IntelligentTieringConfigurations" : [ IntelligentTieringConfiguration, ... ],
        #  TODO:     "InventoryConfigurations" : [ InventoryConfiguration, ... ],
        #  TODO:     "LifecycleConfiguration" : LifecycleConfiguration,
        #  TODO:     "LoggingConfiguration" : LoggingConfiguration,
        #  TODO:     "MetricsConfigurations" : [ MetricsConfiguration, ... ],
        #  TODO:     "NotificationConfiguration" : NotificationConfiguration,
        #  TODO:     "OwnershipControls" : OwnershipControls,
        #  TODO:     "ReplicationConfiguration" : ReplicationConfiguration,
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

        # Analytics Configurations
        analy_set = s3.list_bucket_analytics_configurations(**self._bucket_filter)
        if "AnalyticsConfigurationList" in analy_set:
            a_cfgs = []
            for analy_config in analy_set["AnalyticsConfigurationList"]:
                cfg = {"Id": analy_config["Id"] }

                if "Prefix" in analy_config :
                    cfg["Prefix"] = analy_config["Prefix"]

                # Filters are moderately complicated.
                if "Filter" in analy_config:
                    # Case 1: Tag alone (and singular)
                    if "Tag" in analy_config["Filter"]:
                        cfg["TagFilters"] = [ analy_config["Filter"]["Tag"] ]
                    # Case 2: Prefix alone
                    elif "Prefix" in analy_config["Filter"]:
                        cfg["Prefix"] = analy_config["Filter"]["Prefix"]
                    # Case 3: Multiple
                    elif "And" in analy_config["Filter"]:
                        if "Tags" in analy_config["Filter"]["And"]:
                            cfg["TagFilters"] = analy_config["Filter"]["And"]["Tags"]
                        if "Prefix" in analy_config["Filter"]["And"]:
                            cfg["Prefix"] = analy_config["Filter"]["And"]["Prefix"]

                # StorageClassAnalysis is rather more complicated.
                cfg["StorageClassAnalysis"] = {}
                if "DataExport" in analy_config["StorageClassAnalysis"]:
                    src = analy_config["StorageClassAnalysis"]["DataExport"]
                    dst_dx = {
                        "OutputSchemaVersion": src["OutputSchemaVersion"],
                        "Destination": {}
                    }
                    src = src["Destination"]["S3BucketDestination"]

                    dst_dx["Destination"]["Format"] = src["Format"]

                    dst_arn = AwsARN(src["Bucket"])
                    dst_bucket = AwsBucket(self._environment, dst_arn.resource_id)
                    self._environment.add_to_todo(dst_bucket)
                    dst_dx["Destination"]["BucketArn"] = {"Fn::Sub": "arn:aws:s3:::" + dst_bucket.calculate_bucket_name()}

                    if "BucketAccountId" in src:
                        dst_dx["Destination"]["BucketAccountId"] = src["BucketAccountId"]
                    else:
                        dst_dx["Destination"]["BucketAccountId"] = {"Fn::Sub": "${AWS::AccountId}"}
                    if "Prefix" in src:
                        dst_dx["Destination"]["Prefix"] = src["Prefix"]

                    cfg["StorageClassAnalysis"]["DataExport"] = dst_dx

                a_cfgs.append(cfg)
            self._element["AnalyticsConfigurations"] = a_cfgs

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

        # The (Calculated) name
        self._element["BucketName"] = {"Fn::Sub": self.calculate_bucket_name()}

        # Object Lock Configuration
        olc = self.wrap_call(s3.get_object_lock_configuration)
        if olc and olc["ObjectLockConfiguration"]["ObjectLockEnabled"] == "Enabled":
                self._element["ObjectLockEnabled"] = True
                self._element["ObjectLockConfiguration"] = olc["ObjectLockConfiguration"]

        # Public Access Block configuration
        pabc = self.wrap_call(s3.get_public_access_block)
        if pabc:
            self._element["PublicAccessBlockConfiguration"] = pabc["PublicAccessBlockConfiguration"]

        # Tags
        tagging = self.wrap_call(s3.get_bucket_tagging)
        if tagging:
            self._tags.from_api_result(tagging["TagSet"])

        # Versioning
        accc = self.wrap_call(s3.get_bucket_versioning)
        if accc and "Status" in accc:
            self._element["VersioningConfiguration"] = {
                "VersioningStatus": accc["Status"]
            }
            if "MFADelete" in accc and accc["MFADelete"] == "Enabled":
                self._environment.add_warning("MFA Delete cannot be enabled using CFN.", self.physical_id)

        # Do we have a policy?
        bucket_policy = self.wrap_call(s3.get_bucket_policy)
        if bucket_policy:
            self._environment.add_to_todo(
                AwsBucketPolicy(
                    self._environment,
                    original_bucket=self.physical_id,
                    bucket_name=self.calculate_bucket_name(),
                    policy_data=bucket_policy["Policy"]
                )
            )

        self.is_valid = True

    def wrap_call(self, call):
        try:
            result = call(**(self._bucket_filter))
        except Exception as e:
            return None
        return result

    def calculate_bucket_name(self):
        return "${AWS::StackName}-${AWS::AccountId}-${AWS::Region}-" + self.physical_id

