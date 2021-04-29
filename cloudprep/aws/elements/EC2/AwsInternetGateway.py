import boto3

from ...VpcAttachmentRegistry import VpcAttachmentRegistry
from .AwsVpcGatewayAttachment import AwsVpcGatewayAttachment
from .RouteTarget import RouteTarget
from cloudprep.aws.elements.TagSet import TagSet


class AwsInternetGateway(RouteTarget):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__("AWS::EC2::InternetGateway", environment, physical_id, **kwargs)

    @RouteTarget.capture_method
    def capture(self):
        ec2 = boto3.client("ec2")
        if self._source_data is None:
            source_data = ec2.describe_internet_gateways(InternetGatewayIds=[self._physical_id])["InternetGateways"][0]
        else:
            source_data = self._source_data
            self._source_data = None

        self._tags = TagSet({"CreatedBy": "CloudPrep"})
        self._tags.from_api_result(source_data["Tags"])
        vpc = self._route.route_table.vpc

        iga = AwsVpcGatewayAttachment(
            self._environment,
            vpc.physical_id + self.physical_id,
            vpc=vpc
        )
        iga.set_internet_gateway(self)
        VpcAttachmentRegistry.register_attachment(vpc, self, iga)

        self._environment.add_to_todo(iga)

        self.is_valid = True
