import boto3

from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet

class AwsManagedPrefixList(AwsElement):
    def __init__(self,environment, phyiscalId):
        super().__init__( "AWS::EC2::PrefixList", environment, phyiscalId)
        self.setDefaults( { "EnableDnsHostnames": False,
                             "EnableDnsSupport": True,
                            "InstanceTenancy": "default"
                             } )
        self._physical_id = phyiscalId
        self._tags = TagSet({"CreatedBy": "CloudPrep"})

    def capture(self):
        EC2 = boto3.client("ec2")
        #
        sourceJson = EC2.describe_managed_prefix_lists(PrefixListIds=[self._physical_id])["PrefixLists"][0]
        if sourceJson["OwnerId"] == "AWS":
            raise Exception("Prefix list " + self._physical_id + " appears to be AWS-managed.")

        #     "Properties": {
        #         "Entries": [Entry, ...],
        #     }
        # }
        #
        #
        self.copyIfExists("AddressFamily", sourceJson)
        self.copyIfExists("MaxEntries", sourceJson)
        self.copyIfExists("PrefixListName", sourceJson)
        self.copyIfExists("Entries", EC2.get_managed_prefix_list_entries(PrefixListId=self._physical_id))
        self._tags.fromApiResult(sourceJson)
        self.makeValid()

        # self.copyIfExists("InstanceTenancy", sourceJson)
        # self._tags.fromApiResult(sourceJson["Tags"])
        #
        # for attrib in ["enableDnsSupport", "enableDnsHostnames"]:
        #     attribQuery = EC2.describe_vpc_attribute(
        #         VpcId=self._physical_id,
        #         Attribute=attrib
        #     )
        #     attribUC = attrib[0].upper() + attrib[1:]
        #     if not self.isDefault(attribUC, attribQuery[attribUC]["Value"]):
        #         self._element[attribUC] = attribQuery[attribUC]["Value"]
        #
        # for net in EC2.describe_subnets(Filters=[{ "Name": "vpc-id", "Values": [ self._physical_id ]}])["Subnets"]:
        #     self._environment.addToTodo(AwsSubnet(self._environment,net["SubnetId"]))
        #
        # for syg in EC2.describe_security_groups(Filters=[{ "Name": "vpc-id", "Values": [ self._physical_id ]}])["SecurityGroups"]:
        #     if syg["GroupName"] != "default":
        #         self._environment.addToTodo(AwsSecurityGroup(self._environment,syg["GroupId"]))
