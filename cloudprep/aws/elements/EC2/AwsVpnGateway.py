import boto3

from .RouteTarget import RouteTarget
from cloudprep.aws.elements.TagSet import TagSet
from ...VpcAttachmentRegistry import VpcAttachmentRegistry
from .AwsVpcGatewayAttachment import AwsVpcGatewayAttachment

class AwsVpnGateway(RouteTarget):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__("AWS::EC2::VPNGateway", environment, physical_id, **kwargs)
        self.set_defaults({"AmazonSideAsn": 64512})
        self._tags = TagSet({"CreatedBy": "CloudPrep"})

    @RouteTarget.capture_method
    def capture(self):
        ec2 = boto3.client("ec2")
        source_data = ec2.describe_vpn_gateways(VpnGatewayIds=[self._physical_id])["VpnGateways"][0]

        self.copy_if_exists("AmazonSideAsn", source_data)
        self.copy_if_exists("Type", source_data)
        self._tags.from_api_result(source_data)

        # TODO: Capture VGW Routes and Route Tables.

        # TODO: Map to multiple VPCs.
        vpc = self._route.route_table.vpc
        vgw_attachment = AwsVpcGatewayAttachment(
            self._environment,
            vpc.physical_id + self.physical_id,
            vpc=vpc
        )
        vgw_attachment.set_vpn_gateway(self)
        self._environment.add_to_todo(vgw_attachment)
        VpcAttachmentRegistry.register_attachment(self._route.route_table.vpc, self, vgw_attachment)

        self.is_valid = True
