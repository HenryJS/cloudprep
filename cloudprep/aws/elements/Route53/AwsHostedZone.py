import boto3
from ..AwsARN import AwsARN
from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet


class AwsHostedZone(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::S3::HostedZone", physical_id, **kwargs)

    @AwsElement.capture_method
    def capture(self):

        r53 = boto3.client("route53")

        # {
        #     "Type": "AWS::Route53::HostedZone",
        #     "Properties": {
        #         "HostedZoneConfig": HostedZoneConfig,
        #         "HostedZoneTags": [HostedZoneTag, ...],
        #         "Name": String,
        #         "QueryLoggingConfig": QueryLoggingConfig,
        #         "VPCs": [VPC, ...]
        #     }
        # }
        source_data = r53.get_hosted_zone(Id=self.physical_id)["HostedZone"]
        self.copy_if_exists("Name", source_data)

        self.is_valid = True
