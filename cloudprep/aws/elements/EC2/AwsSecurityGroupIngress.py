import boto3

from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.SimpleElement import SimpleElement
from cloudprep.aws.elements.TagSet import TagSet

class AwsSecurityGroupIngress(AwsElement):
    def __init__(self,environment, phyiscalId):
        super().__init__( "AWS::EC2::SecurityGroupIngress", environment)
        # self.setDefaults( { "AssignIpv6AddressOnCreation": False,
        #                      "MapPublicIpOnLaunch": False
        #                      } )
        self._physical_id = None

    def interpret(self, sourceJson):
        for inbound in sourceJson["IpPermissions"]:
            # {
            #   "CidrIpv6" : String,
            #   "FromPort" : Integer,
            #   "IpProtocol" : String,
            #   "SourcePrefixListId" : String,
            #   "SourceSecurityGroupId" : String,
            #   "SourceSecurityGroupName" : String,
            #   "SourceSecurityGroupOwnerId" : String,
            #   "ToPort" : Integer
            # }
            for ipRange in sourceJson["IpRanges"]:
                ingressGroups.append({
                    "CidrIp": ipRange["CidrIp"],
                    "Description": ipRange["Description"],


                })
            inbound["CidrIp" ]

        egressGroups = []

        self._tags.fromApiResult(sourceJson["Tags"])