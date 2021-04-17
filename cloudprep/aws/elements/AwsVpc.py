import boto3

from .AwsElement import AwsElement
from .AwsSubnet import AwsSubnet
from .AwsSecurityGroup import AwsSecurityGroup
from .TagSet import TagSet

class AwsVpc(AwsElement):
    def __init__(self,environment, phyiscalId):
        super().__init__( "AWS::EC2::VPC", environment, phyiscalId)
        self.setDefaults( { "EnableDnsHostnames": False,
                             "EnableDnsSupport": True,
                            "InstanceTenancy": "default"
                             } )
        self._physical_id = phyiscalId
        self._tags = TagSet({"CreatedBy": "CloudPrep"})

    def capture(self):
        EC2 = boto3.client("ec2")
        sourceJson = EC2.describe_vpcs(VpcIds=[self._physical_id])["Vpcs"][0]

        self.copyIfExists("CidrBlock", sourceJson)
        self.copyIfExists("InstanceTenancy", sourceJson)
        self._tags.fromCfn(sourceJson["Tags"])

        for attrib in ["enableDnsSupport", "enableDnsHostnames"]:
            attribQuery = EC2.describe_vpc_attribute(
                VpcId=self._physical_id,
                Attribute=attrib
            )
            attribUC = attrib[0].upper() + attrib[1:]
            if not self.isDefault(attribUC, attribQuery[attribUC]["Value"]):
                self._element[attribUC] = attribQuery[attribUC]["Value"]

        for net in EC2.describe_subnets(Filters=[{ "Name": "vpc-id", "Values": [ self._physical_id ]}])["Subnets"]:
            self._environment.addToTodo(AwsSubnet(self._environment,net["SubnetId"]))

        for syg in EC2.describe_security_groups(Filters=[{ "Name": "vpc-id", "Values": [ self._physical_id ]}])["SecurityGroups"]:
            if syg["GroupName"] != "default":
                self._environment.addToTodo(AwsSecurityGroup(self._environment,syg["GroupId"]))
