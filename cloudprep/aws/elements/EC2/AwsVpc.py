import boto3

from cloudprep.aws.elements.AwsElement import AwsElement
from .AwsSubnet import AwsSubnet
from .AwsSecurityGroup import AwsSecurityGroup
from .AwsInternetGateway import AwsInternetGateway
from cloudprep.aws.elements.TagSet import TagSet


class AwsVpc(AwsElement):
    def __init__(self, environment, physical_id):
        super().__init__("AWS::EC2::VPC", environment, physical_id)
        self.set_defaults({
            "EnableDnsHostnames": False,
            "EnableDnsSupport": True,
            "InstanceTenancy": "default"
        })
        self._physical_id = physical_id
        self._tags = TagSet({"CreatedBy": "CloudPrep"})

    def capture(self):
        ec2 = boto3.client("ec2")
        source_json = ec2.describe_vpcs(VpcIds=[self._physical_id])["Vpcs"][0]

        self.copy_if_exists("CidrBlock", source_json)
        self.copy_if_exists("InstanceTenancy", source_json)
        self._tags.from_api_result(source_json["Tags"])

        for attrib in ["enableDnsSupport", "enableDnsHostnames"]:
            attrib_query = ec2.describe_vpc_attribute(
                VpcId=self._physical_id,
                Attribute=attrib
            )
            attrib_uc = attrib[0].upper() + attrib[1:]
            if not self.is_default(attrib_uc, attrib_query[attrib_uc]["Value"]):
                self._element[attrib_uc] = attrib_query[attrib_uc]["Value"]

        for net in ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [self._physical_id]}])["Subnets"]:
            self._environment.add_to_todo(AwsSubnet(self._environment, net["SubnetId"], net))

        for syg in ec2.describe_security_groups(
                Filters=[{"Name": "vpc-id", "Values": [self._physical_id]}]
        )["SecurityGroups"]:
            if syg["GroupName"] != "default":
                self._environment.add_to_todo(
                    AwsSecurityGroup(
                        self._environment,
                        syg["GroupId"],
                        syg
                    ))

        for igw in ec2.describe_internet_gateways(
                Filters=[{"Name": "attachment.vpc-id", "Values": [self._physical_id]}]
        )["InternetGateways"]:
            aws_igw = AwsInternetGateway(self._environment, igw["InternetGatewayId"], self, igw)
            self._environment.add_to_todo(aws_igw)

        self.make_valid()

