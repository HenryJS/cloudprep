import boto3

from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet


class AwsSubnet(AwsElement):
    def __init__(self, environment, physical_id):
        super().__init__("AWS::EC2::Subnet", environment, physical_id)
        self.set_defaults({
            "AssignIpv6AddressOnCreation": False,
            "MapPublicIpOnLaunch": False
        })
        self._physical_id = physical_id
        self._tags = TagSet({"CreatedBy": "CloudPrep"})

    def capture(self):
        ec2 = boto3.client("ec2")
        source_json = ec2.describe_subnets(SubnetIds=[self._physical_id])["Subnets"][0]

        self._element["AssignIpv6AddressOnCreation"] = source_json["AssignIpv6AddressOnCreation"]
        self._element["AvailabilityZone"] = self.abstract_az(source_json["AvailabilityZone"])
        self._element["CidrBlock"] = source_json["CidrBlock"]
        self._element["MapPublicIpOnLaunch"] = source_json["MapPublicIpOnLaunch"]

        if len(source_json["Ipv6CidrBlockAssociationSet"]) > 0:
            self._element["Ipv6CidrBlock"] = source_json["Ipv6CidrBlockAssociationSet"][0]

        self.copy_if_exists("OutpostArn", source_json)

        self._element["VpcId"] = {"Ref": (self._environment.logical_from_physical(source_json["VpcId"]))}

        self._tags.from_api_result(source_json["Tags"])

        self.make_valid()

    @staticmethod
    def abstract_az(az_name):
        letter = az_name[-1]
        position = ord(letter)-ord('a')
        return {
                "Fn::Select": [position, {"Fn::GetAZs": ""}]
        }

