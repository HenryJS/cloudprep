from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet


class AwsTransitGatewayVpcAttachment(AwsElement):

    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::EC2::TransitGatewayAttachment", physical_id, **kwargs)
        self.set_defaults({})
        self._tags = TagSet()

    @AwsElement.capture_method
    def capture(self):
        if self._source_data is None:
            source_data = None
            pass
        else:
            source_data = self._source_data
            self._source_data = None

        if source_data and source_data["State"] not in ["available", "pending"]:
            return

        self.refer_if_exists("VpcId", source_data)
        self.refer_if_exists("TransitGatewayId", source_data)
        self.array_refer_if_exists("SubnetIds", source_data)

        self.is_valid = True

