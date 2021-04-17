import boto3

from .AwsElement import AwsElement
from cloudprep.aws.SimpleElement import SimpleElement
from .TagSet import TagSet

class AwsSecurityGroup(AwsElement):
    def __init__(self,environment, phyiscalId):
        super().__init__( "AWS::EC2::SecurityGroup", environment, phyiscalId)
        # self.setDefaults( { "AssignIpv6AddressOnCreation": False,
        #                      "MapPublicIpOnLaunch": False
        #                      } )
        self._physical_id = phyiscalId
        self._tags = TagSet({"CreatedBy": "CloudPrep"})


    def capture(self):
        EC2 = boto3.client("ec2")
        sourceJson = EC2.describe_security_groups(GroupIds=[self._physical_id])["SecurityGroups"][0]
        self._element["GroupDescription"] = sourceJson["Description"]
        self._element["GroupName"] = sourceJson["GroupName"]
        self._element["VpcId"] = { "Ref" : self._environment.logicalFromPhysical(sourceJson["VpcId"]) }
        if "Tags" in sourceJson:
            self._tags.fromCfn(sourceJson["Tags"])


        ingressRules = []
        for inbound in sourceJson["IpPermissions"]:
            # {{
            # Works for: PURE IPv4 SYGs.
            # TODO: IPv6 and PrefixLists
            #   "CidrIpv6" : String,
            #   "SourcePrefixListId" : String,
            # }
            for ipRange in inbound["IpRanges"]:
                thisRule = {}
                for key in ["IpProtocol", "ToPort", "FromPort"]:
                    if key in inbound:
                        thisRule[key] = inbound[key]
                for key in ["Description", "CidrIp"]:
                    if key in ipRange:
                        thisRule[key] = ipRange[key]
                ingressRules.append(thisRule)

            for ip6Range in inbound["Ipv6Ranges"]:
                thisRule = {}
                for key in ["IpProtocol", "ToPort", "FromPort"]:
                    if key in inbound:
                        thisRule[key] = inbound[key]
                for key in ["Description", "CidrIpv6"]:
                    if key in ip6Range:
                        thisRule[key] = ip6Range[key]
                ingressRules.append(thisRule)

            for userPair in inbound["UserIdGroupPairs"]:
                thisRule = {}
                for key in ["IpProtocol", "ToPort", "FromPort"]:
                    if key in inbound:
                        thisRule[key] = inbound[key]
                if "Description" in userPair:
                    thisRule["Description"] = userPair["Description"]
                if "UserId" in userPair:
                    thisRule["SourceSecurityGroupOwnerId"] = userPair["UserId"]
                if "GroupId" in userPair:
                    thisRule["SourceSecurityGroupId"] = {"Ref": AwsElement.CalculateLogicalId("AWS::EC2::SecurityGroup", userPair["GroupId"]) }


                ingressRules.append(thisRule)

        self._element["SecurityGroupIngress"] = ingressRules

