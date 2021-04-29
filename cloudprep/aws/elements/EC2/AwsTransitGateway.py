import boto3

from .RouteTarget import RouteTarget
from cloudprep.aws.elements.TagSet import TagSet
from ...VpcAttachmentRegistry import VpcAttachmentRegistry
from .AwsTransitGatewayVpcAttachment import AwsTransitGatewayVpcAttachment


class AwsTransitGateway(RouteTarget):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__("AWS::EC2::TransitGateway", environment, physical_id, **kwargs)
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

    @RouteTarget.capture_method
    def capture(self):
        ec2 = boto3.client("ec2")
        source_data = ec2.describe_transit_gateways(TransitGatewayIds=[self._physical_id])["TransitGateways"][0]

        self.copy_if_exists("Description", source_data)
        self.copy_if_exists("AmazonSideAsn", source_data["Options"])
        self.copy_if_exists("AutoAcceptSharedAttachments", source_data["Options"])
        self.copy_if_exists("DefaultRouteTableAssociation", source_data["Options"])
        self.copy_if_exists("DefaultRouteTablePropagation", source_data["Options"])
        # TODO: If Multicast is true, capture the domain and the attachment (then spider!)
        self.copy_if_exists("MulticastSupport", source_data["Options"])
        self.copy_if_exists("VpnEcmpSupport", source_data["Options"])
        self.copy_if_exists("DnsSupport", source_data["Options"])

        self._tags.from_api_result(source_data)

        # TODO: Capture TGW Routes and Route Tables.

        attachments = ec2.describe_transit_gateway_vpc_attachments()["TransitGatewayVpcAttachments"]
        for attachment in [x for x in attachments if x["TransitGatewayId"] == self.physical_id]:
            tgva = AwsTransitGatewayVpcAttachment(
                self._environment,
                attachment["TransitGatewayAttachmentId"],
                source_data=attachment
            )
            self._environment.add_to_todo(tgva)

            VpcAttachmentRegistry.register_attachment(self._route.route_table.vpc, self, tgva)

        self.is_valid = True
