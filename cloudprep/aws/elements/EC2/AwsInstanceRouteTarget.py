import boto3

from .RouteTarget import RouteTarget
from cloudprep.aws.elements.TagSet import TagSet
from ...VpcAttachmentRegistry import VpcAttachmentRegistry
from .AwsVpcGatewayAttachment import AwsVpcGatewayAttachment

class AwsInstanceRouteTarget(RouteTarget):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__("NoType", environment, physical_id, **kwargs)
        self.set_defaults({})
        self._tags = TagSet()

    @RouteTarget.capture_method
    def capture(self):
        # TODO: Capture an Instance Route Target
        self.is_valid = False
