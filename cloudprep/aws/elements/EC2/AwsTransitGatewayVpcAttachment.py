from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet


class AwsTransitGatewayVpcAttachment(AwsElement):

    def __init__(self, environment, physical_id, source_json=None):
        super().__init__(environment, "AWS::EC2::TransitGatewayAttachment", physical_id, source_json)
        self.set_defaults({})
        self._tags = TagSet({"CreatedBy": "CloudPrep"})

    @AwsElement.capture_method
    def capture(self):
        if self._source_json is None:
            source_json = None
            pass
        else:
            source_json = self._source_json
            self._source_json = None

        if source_json["State"] not in ["available", "pending"]:
            return

        self.refer_if_exists("VpcId", source_json)
        self.refer_if_exists("TransitGatewayId", source_json)
        self.array_refer_if_exists("SubnetIds", source_json)

        self.make_valid()

