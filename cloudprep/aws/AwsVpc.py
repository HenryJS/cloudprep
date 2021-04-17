import boto3

from .AwsElement import AwsElement

class AwsVpc(AwsElement):
    def __init__(self,environment):
        super().__init__( "AWS::EC2::VPC", environment)
        self.setDefaults( { "EnableDnsHostnames": False,
                             "EnableDnsSupport": True
                             } )


    def capture(self, sourceJson):
        self._physical_id = sourceJson["VpcId"]

        self._element["CidrBlock"] = sourceJson["CidrBlock"]
        self._element["InstanceTenancy"] = sourceJson["InstanceTenancy"]
        self._element["Tags"] = self._sanitiseTags(sourceJson["Tags"])
        self._element["Tags"].append({"Key":"CreatedBy","Value":"CloudPrep"})

        EC2 = boto3.client("ec2")
        for attrib in ["enableDnsSupport", "enableDnsHostnames"]:
            attribQuery = EC2.describe_vpc_attribute(
                VpcId=self._physical_id,
                Attribute=attrib
            )
            attribUC = attrib[0].upper() + attrib[1:]
            if not self.isDefault(attribUC, attribQuery[attribUC]["Value"]):
                self._element[attribUC] = attribQuery[attribUC]["Value"]
