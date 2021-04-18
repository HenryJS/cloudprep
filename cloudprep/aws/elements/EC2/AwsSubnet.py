import boto3

from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet


class AwsSubnet(AwsElement):
    def __init__(self, environment, phyiscalId):
        super().__init__("AWS::EC2::Subnet", environment, phyiscalId)
        self.setDefaults({
            "AssignIpv6AddressOnCreation": False,
            "MapPublicIpOnLaunch": False
        })
        self._physical_id = phyiscalId
        self._tags = TagSet({"CreatedBy": "CloudPrep"})

    def capture(self):
        EC2 = boto3.client("ec2")
        sourceJson = EC2.describe_subnets(SubnetIds=[self._physical_id])["Subnets"][0]

        self._element["AssignIpv6AddressOnCreation"] = sourceJson["AssignIpv6AddressOnCreation"]
        self._element["AvailabilityZone"] = self.abstractAz(sourceJson["AvailabilityZone"])
        self._element["CidrBlock"] = sourceJson["CidrBlock"]
        self._element["MapPublicIpOnLaunch"] = sourceJson["MapPublicIpOnLaunch"]

        if len(sourceJson["Ipv6CidrBlockAssociationSet"]) > 0:
            self._element["Ipv6CidrBlock"] = sourceJson["Ipv6CidrBlockAssociationSet"][0]

        self.copyIfExists("OutpostArn", sourceJson)

        self._element["VpcId"] = {"Ref": (self._environment.logicalFromPhysical(sourceJson["VpcId"]))}

        self._tags.from_api_result(sourceJson["Tags"])

        self.makeValid()

    def abstractAz(self, azName):
        letter = azName[-1]
        position = ord(letter)-ord('a')
        return {
                "Fn::Select": [position, {"Fn::GetAZs": ""}]
        }

