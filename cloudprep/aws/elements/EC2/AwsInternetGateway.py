import boto3

from ...VpcAttachmentRegistry import VpcAttachmentRegistry
from .AwsVpcGatewayAttachment import AwsVpcGatewayAttachment
from .RouteTarget import RouteTarget
from cloudprep.aws.elements.TagSet import TagSet


class AwsInternetGateway(RouteTarget):
    def __init__(self, environment, physical_id, route):
        super().__init__("AWS::EC2::InternetGateway", environment, physical_id, route)

    def local_capture(self):
        ec2 = boto3.client("ec2")
        if self._source_json is None:
            source_json = ec2.describe_internet_gateways(InternetGatewayIds=[self._physical_id])["InternetGateways"][0]
        else:
            source_json = self._source_json
            self._source_json = None

        self._tags = TagSet({"CreatedBy": "CloudPrep"})
        self._tags.from_api_result(source_json["Tags"])
        vpc = self._route.get_route_table().get_vpc()

        iga = AwsVpcGatewayAttachment(
            self._environment,
            vpc.physical_id + self.physical_id,
            vpc
        )
        iga.set_internet_gateway(self)
        VpcAttachmentRegistry.register_attachment(vpc, self, iga)

        self._environment.add_to_todo(iga)

        self.make_valid()
