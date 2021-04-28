import boto3

from cloudprep.aws.elements.AwsElement import AwsElement
from .AwsManagedPrefixList import AwsManagedPrefixList
from cloudprep.aws.elements.TagSet import TagSet


class AwsSecurityGroup(AwsElement):
    def __init__(self, environment, physical_id, source_json=None):
        super().__init__("AWS::EC2::SecurityGroup", environment, physical_id, source_json)
        self._physical_id = physical_id
        self._tags = TagSet({"CreatedBy": "CloudPrep"})

    def local_capture(self):
        ec2 = boto3.client("ec2")
        if self._source_json is None:
            source_json = ec2.describe_security_groups(GroupIds=[self._physical_id])["SecurityGroups"][0]
        else:
            source_json = self._source_json
            self._source_json = None

        self._element["GroupDescription"] = source_json["Description"]
        self._element["VpcId"] = self._environment.find_by_physical_id(source_json["VpcId"]).make_reference()

        if source_json["GroupName"] == "default":
            self._element["GroupName"] = "was-default"
        else:
            self._element["GroupName"] = source_json["GroupName"]

        if "Tags" in source_json:
            self._tags.from_api_result(source_json)

        ingress_rules = IngressRuleset(self._environment)
        ingress_rules.process(source_json["OwnerId"], source_json["IpPermissions"])
        self._element["SecurityGroupIngress"] = ingress_rules.data

        egress_rules = EgressRuleset(self._environment)
        egress_rules.process(source_json["OwnerId"], source_json["IpPermissionsEgress"])
        self._element["SecurityGroupEgress"] = egress_rules.data

        self.make_valid()


class Ruleset:
    def __init__(self, environment):
        self.data = []
        self._environment = environment
        self._groupIdKey = "NoGroupIdKey"
        self._prefixListIdKey = "NoPrefixListIdKey"

    def process(self, owner_id, source_json):
        for rule in source_json:
            # Process IPv4 rules.  These are the same between Egress and Ingress.
            for ipRange in rule["IpRanges"]:
                this_rule = {}
                for key in ["IpProtocol", "ToPort", "FromPort"]:
                    if key in rule:
                        this_rule[key] = rule[key]
                for key in ["Description", "CidrIp"]:
                    if key in ipRange:
                        this_rule[key] = ipRange[key]
                self.data.append(this_rule)

            # Process IPv6 rules.  These are the same between Egress and Ingress.
            for ip6Range in rule["Ipv6Ranges"]:
                this_rule = {}
                for key in ["IpProtocol", "ToPort", "FromPort"]:
                    if key in rule:
                        this_rule[key] = rule[key]
                for key in ["Description", "CidrIpv6"]:
                    if key in ip6Range:
                        this_rule[key] = ip6Range[key]
                self.data.append(this_rule)

            # Process SecurityGroup related rules.
            for userPair in rule["UserIdGroupPairs"]:
                this_rule = {}
                for key in ["IpProtocol", "ToPort", "FromPort"]:
                    if key in rule:
                        this_rule[key] = rule[key]
                if "Description" in userPair:
                    this_rule["Description"] = userPair["Description"]

                # UserID only applies to inbound rules; this condition will be false for outbound rules.
                if "UserId" in userPair and userPair["UserId"] != owner_id:
                    this_rule["SourceSecurityGroupOwnerId"] = userPair["UserId"]

                if "GroupId" in userPair:
                    this_rule[self._groupIdKey] = {
                        "Ref": AwsElement.calculate_logical_id(userPair["GroupId"])
                    }

                self.data.append(this_rule)

            for prefixList in rule["PrefixListIds"]:
                this_rule = {}
                for key in ["IpProtocol", "ToPort", "FromPort"]:
                    if key in rule:
                        this_rule[key] = rule[key]
                if "Description" in prefixList:
                    this_rule["Description"] = prefixList["Description"]
                if "PrefixListId" in prefixList:
                    this_rule[self._prefixListIdKey] = {
                        "Ref": AwsElement.calculate_logical_id(prefixList["PrefixListId"])
                    }
                    self._environment.add_to_todo(AwsManagedPrefixList(self._environment, prefixList["PrefixListId"]))
                self.data.append(this_rule)


class IngressRuleset(Ruleset):
    def __init__(self, environment):
        super().__init__(environment)
        self._groupIdKey = "SourceSecurityGroupId"
        self._prefixListIdKey = "SourcePrefixListId"


class EgressRuleset(Ruleset):
    def __init__(self, environment):
        super().__init__(environment)
        self._groupIdKey = "DestinationSecurityGroupId"
        self._prefixListIdKey = "DestinationPrefixListId"

