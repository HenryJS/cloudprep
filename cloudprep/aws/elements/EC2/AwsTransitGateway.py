import boto3

from .RouteTarget import RouteTarget
from cloudprep.aws.elements.TagSet import TagSet
from ...VpcAttachmentRegistry import VpcAttachmentRegistry
from .AwsTransitGatewayVpcAttachment import AwsTransitGatewayVpcAttachment


class AwsTransitGateway(RouteTarget):
    def __init__(self, environment, physical_id, route=None):
        super().__init__("AWS::EC2::TransitGateway", environment, physical_id, route)
        self.set_defaults({
            "AmazonSideAsn": 64512,
            "AutoAcceptSharedAttachments": "disable",
            "DefaultRouteTableAssociation": "enable",
            "DefaultRouteTablePropagation": "enable",
            "DnsSupport": "enable",
            "VpnEcmpSupport": "enable",
            "MulticastSupport": "disable"
        })
        self._tags = TagSet({"CreatedBy": "CloudPrep"})

    def local_capture(self):
        ec2 = boto3.client("ec2")
        source_json = ec2.describe_transit_gateways(TransitGatewayIds=[self._physical_id])["TransitGateways"][0]

        self.copy_if_exists("Description", source_json)
        self.copy_if_exists("AmazonSideAsn", source_json["Options"])
        self.copy_if_exists("AutoAcceptSharedAttachments", source_json["Options"])
        self.copy_if_exists("DefaultRouteTableAssociation", source_json["Options"])
        self.copy_if_exists("DefaultRouteTablePropagation", source_json["Options"])
        # TODO: If Multicast is true, capture the domain and the attachment (then spider!)
        self.copy_if_exists("MulticastSupport", source_json["Options"])
        self.copy_if_exists("VpnEcmpSupport", source_json["Options"])
        self.copy_if_exists("DnsSupport", source_json["Options"])

        self._tags.from_api_result(source_json)

        # TODO: Capture TGW Routes and Route Tables.

        attachments = ec2.describe_transit_gateway_vpc_attachments()["TransitGatewayVpcAttachments"]
        for attachment in attachments:
            tgva = AwsTransitGatewayVpcAttachment(
                self._environment,
                attachment["TransitGatewayAttachmentId"],
                attachment
            )
            self._environment.add_to_todo(tgva)

            VpcAttachmentRegistry.register_attachment(self._route.get_route_table().get_vpc(), self, tgva)

        self.make_valid()
