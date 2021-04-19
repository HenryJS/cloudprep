import boto3

from cloudprep.aws.elements.AwsElement import AwsElement
from .AwsVpcGatewayAttachment import AwsVpcGatewayAttachment
from cloudprep.aws.elements.TagSet import TagSet


class AwsInternetGateway(AwsElement):
    def __init__(self, environment, physical_id, vpc, source_json=None):
        super().__init__("AWS::EC2::InternetGateway", environment, physical_id, source_json)
        self._attached_vpc = vpc

    def capture(self):
        ec2 = boto3.client("ec2")
        if self._source_json is None:
            source_json = ec2.describe_internet_gateways(InternetGatewayId=self._physical_id)["InternetGateways"][0]
        else:
            source_json = self._source_json
            self.set_source_json(None)

        self._tags = TagSet({"CreatedBy": "CloudPrep"})
        self._tags.from_api_result(source_json["Tags"])

        iga = AwsVpcGatewayAttachment(
            self._environment,
            self._attached_vpc.get_physical_id() + self.get_physical_id(),
            self._attached_vpc
        )
        iga.set_internet_gateway(self)
        self._environment.add_to_todo(iga)

        self.make_valid()
