import boto3

from .AwsElement import AwsElement
from .SimpleElement import SimpleElement

class AwsVpc(AwsElement):
    def __init__(self,environment, phyiscalId):
        super().__init__( "AWS::EC2::VPC", environment)
        self.setDefaults( { "EnableDnsHostnames": False,
                             "EnableDnsSupport": True
                             } )
        self._physical_id = phyiscalId


    def capture(self):
        EC2 = boto3.client("ec2")
        sourceJson = EC2.describe_vpcs(VpcIds=[self._physical_id])["Vpcs"][0]

        self._element["CidrBlock"] = sourceJson["CidrBlock"]
        self._element["InstanceTenancy"] = sourceJson["InstanceTenancy"]
        self._element["Tags"] = self._sanitiseTags(sourceJson["Tags"])
        self._element["Tags"].append({"Key":"CreatedBy","Value":"CloudPrep"})

        for attrib in ["enableDnsSupport", "enableDnsHostnames"]:
            attribQuery = EC2.describe_vpc_attribute(
                VpcId=self._physical_id,
                Attribute=attrib
            )
            attribUC = attrib[0].upper() + attrib[1:]
            if not self.isDefault(attribUC, attribQuery[attribUC]["Value"]):
                self._element[attribUC] = attribQuery[attribUC]["Value"]

        subnets = EC2.describe_subnets(Filters=[
            { "Name": "vpc-id", "Values": [ self._physical_id ]}
        ])["Subnets"]
        for net in subnets:
            self._environment.addToTodo(SimpleElement(self._environment,net["SubnetId"]))