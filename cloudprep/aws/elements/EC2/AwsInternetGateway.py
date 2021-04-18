import boto3

from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet


class AwsInternetGateway(AwsElement):
    def __init__(self, environment, physical_id, vpc):
        super().__init__("AWS::EC2::InternetGateway", environment, physical_id)
        self._attached_vpc = vpc

    def capture(self):
        EC2 = boto3.client("ec2")
        if self._source_json is not None:
            source_json = self._source_json
            self.set_source_json(None)
        else:
            source_json = EC2.describe_internet_gateways(InternetGatewayId=self._physical_id)["InternetGateways"][0]
        self._tags = TagSet({"CreatedBy":"CloudPrep"})
        self._tags.from_api_result(source_json["Tags"])

        iga = AwsVpcGatewayAttachment(self._environment, self._physical_id)
        iga.set_source_json(source_json["Attachments"][0])

        self._environment.addToTodo(iga)

        self.makeValid()


class AwsVpcGatewayAttachment(AwsElement):
    def __init__(self, environment, physical_id):
        super().__init__("AWS::EC2::VpcGatewayAttachment", environment, physical_id)

    def capture(self):
        # ToDo: Make these !Refs
        self._element["VpcId"] = self._source_json["VpcId"]
        self._element["InternetGatewayId"] = self._physical_id
        self.makeValid()
        pass