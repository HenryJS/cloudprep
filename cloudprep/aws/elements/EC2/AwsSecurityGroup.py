import boto3

from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.SimpleElement import SimpleElement
from .AwsManagedPrefixList import AwsManagedPrefixList
from cloudprep.aws.elements.TagSet import TagSet

class AwsSecurityGroup(AwsElement):
    def __init__(self,environment, phyiscalId):
        super().__init__( "AWS::EC2::SecurityGroup", environment, phyiscalId)
        self._physical_id = phyiscalId
        self._tags = TagSet({"CreatedBy": "CloudPrep"})


    def capture(self):
        EC2 = boto3.client("ec2")
        sourceJson = EC2.describe_security_groups(GroupIds=[self._physical_id])["SecurityGroups"][0]
        self._element["GroupDescription"] = sourceJson["Description"]
        self._element["GroupName"] = sourceJson["GroupName"]
        self._element["VpcId"] = { "Ref" : self._environment.logicalFromPhysical(sourceJson["VpcId"]) }
        if "Tags" in sourceJson:
            self._tags.fromApiResult(sourceJson)

        ingressRules = IngressRulest(self._environment)
        ingressRules.process(sourceJson["OwnerId"], sourceJson["IpPermissions"])
        self._element["SecurityGroupIngress"] = ingressRules.data

        egressRules = EgressRulest(self._environment)
        egressRules.process(sourceJson["OwnerId"], sourceJson["IpPermissionsEgress"])
        self._element["SecurityGroupEgress"] = egressRules.data

        self.makeValid()


class Ruleset:
    def __init__(self, environment):
        self.data = []
        self._environment = environment
        self._groupIdKey = "NoGroupIdKey"
        self._prefixListIdKey = "NoPrefixListIdKey"

    def process(self, ownerId, sourceJson):
        for rule in sourceJson:
            # Process IPv4 rules.  These are the same between Egress and Ingress.
            for ipRange in rule["IpRanges"]:
                thisRule = {}
                for key in ["IpProtocol", "ToPort", "FromPort"]:
                    if key in rule:
                        thisRule[key] = rule[key]
                for key in ["Description", "CidrIp"]:
                    if key in ipRange:
                        thisRule[key] = ipRange[key]
                self.data.append(thisRule)

            # Process IPv6 rules.  These are the same between Egress and Ingress.
            for ip6Range in rule["Ipv6Ranges"]:
                thisRule = {}
                for key in ["IpProtocol", "ToPort", "FromPort"]:
                    if key in rule:
                        thisRule[key] = rule[key]
                for key in ["Description", "CidrIpv6"]:
                    if key in ip6Range:
                        thisRule[key] = ip6Range[key]
                self.data.append(thisRule)

            # Process SecurityGroup related rules.  These differ in Security Gropu ID Nameare the same between Egress and Ingress.
            for userPair in rule["UserIdGroupPairs"]:
                thisRule = {}
                for key in ["IpProtocol", "ToPort", "FromPort"]:
                    if key in rule:
                        thisRule[key] = rule[key]
                if "Description" in userPair:
                    thisRule["Description"] = userPair["Description"]

                if "UserId" in userPair and userPair["UserId"] != ownerId:
                    thisRule["SourceSecurityGroupOwnerId"] = userPair["UserId"]

                if "GroupId" in userPair:
                    thisRule[self._groupIdKey] = {
                        "Ref": AwsElement.CalculateLogicalId("AWS::EC2::SecurityGroup", userPair["GroupId"])}

                self.data.append(thisRule)

            for prefixList in rule["PrefixListIds"]:
                thisRule = {}
                for key in ["IpProtocol", "ToPort", "FromPort"]:
                    if key in rule:
                        thisRule[key] = rule[key]
                if "Description" in prefixList:
                    thisRule["Description"] = prefixList["Description"]
                if "PrefixListId" in prefixList:
                    thisRule[self._prefixListIdKey] = {
                        "Ref": AwsElement.CalculateLogicalId("AWS::EC2::PrefixList", prefixList["PrefixListId"])}
                    self._environment.addToTodo(AwsManagedPrefixList(self._environment, prefixList["PrefixListId"]))
                self.data.append(thisRule)

    def ruleSpecialisation(self,sourceJson):
        raise NotImplementedError("Invoked on base class")


class IngressRulest(Ruleset):
    def __init__(self, environment):
        super().__init__(environment)
        self._groupIdKey = "SourceSecurityGroupId"
        self._prefixListIdKey = "SourcePrefixListId"

    def ruleSpecialisation(self,rule):
        pass

class EgressRulest(Ruleset):
    def __init__(self, environment):
        super().__init__(environment)
        self._groupIdKey = "DestinationSecurityGroupId"
        self._prefixListIdKey = "DestinationPrefixListId"

    def ruleSpecialisation(self, rule):
        pass
