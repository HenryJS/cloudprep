import boto3
import sys

from cloudprep.aws.elements.AwsElement import AwsElement
from .AwsManagedPrefixList import AwsManagedPrefixList
from cloudprep.aws.elements.TagSet import TagSet


class AwsSecurityGroup(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::EC2::SecurityGroup", physical_id, **kwargs)
        self._physical_id = physical_id
        self._tags = TagSet()

    @AwsElement.capture_method
    def capture(self):
        ec2 = boto3.client("ec2")
        if self._source_data is None:
            source_data = ec2.describe_security_groups(GroupIds=[self._physical_id])["SecurityGroups"][0]
        else:
            source_data = self._source_data
            self._source_data = None

        self._element["GroupDescription"] = source_data["Description"]
        self._element["VpcId"] = self._environment.find_by_physical_id(source_data["VpcId"]).make_reference()

        if source_data["GroupName"] == "default":
            self._element["GroupName"] = "was-default"
        else:
            self._element["GroupName"] = source_data["GroupName"]

        if "Tags" in source_data:
            self._tags.from_api_result(source_data)

        ingress_rules = IngressRuleset(self._environment, self)
        ingress_rules.process(source_data["OwnerId"], source_data["IpPermissions"])
        self._element["SecurityGroupIngress"] = ingress_rules.data

        egress_rules = EgressRuleset(self._environment, self)
        egress_rules.process(source_data["OwnerId"], source_data["IpPermissionsEgress"])
        self._element["SecurityGroupEgress"] = egress_rules.data

        self.is_valid = True


class Ruleset:
    def __init__(self, environment, parent, rule_class):
        self.data = []
        self._environment = environment
        self._groupIdKey = "NoGroupIdKey"
        self._prefixListIdKey = "NoPrefixListIdKey"
        self._rule_class = rule_class
        self._parent = parent

    @property
    def parent(self):
        return self._parent

    def process(self, owner_id, source_data):
        rule_number = 0

        for rule in source_data:

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
                this_rule = self._rule_class(self._environment, self._parent.physical_id + "-" + str(rule_number))
                this_rule.parent = self
                for key in ["IpProtocol", "ToPort", "FromPort"]:
                    if key in rule:
                        this_rule.properties[key] = rule[key]
                if "Description" in userPair:
                    this_rule.properties["Description"] = userPair["Description"]

                # UserID only applies to inbound rules; this condition will be false for outbound rules.
                if "UserId" in userPair and userPair["UserId"] != owner_id:
                    this_rule.properties["SourceSecurityGroupOwnerId"] = userPair["UserId"]

                if "GroupId" in userPair:
                    this_rule.properties[self._groupIdKey] = {
                        "Ref": AwsElement.calculate_logical_id(userPair["GroupId"])
                    }

                # self.data.append(this_rule)
                self._environment.add_to_todo(this_rule)

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

            rule_number = rule_number + 1


class IngressRuleset(Ruleset):
    def __init__(self, environment, parent):
        super().__init__(environment, parent, AwsSecurityGroupIngress)
        self._groupIdKey = "SourceSecurityGroupId"
        self._prefixListIdKey = "SourcePrefixListId"


class EgressRuleset(Ruleset):
    def __init__(self, environment, parent):
        super().__init__(environment, parent, AwsSecurityGroupEgress)
        self._groupIdKey = "DestinationSecurityGroupId"
        self._prefixListIdKey = "DestinationPrefixListId"


class AwsSecurityGroupRule(AwsElement):
    def __init__(self, environment, aws_type, physical_id, **kwargs):
        super().__init__(environment, aws_type, physical_id, **kwargs)

        self._parent = None

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    def capture_method(f):
        @AwsElement.capture_method
        def transformed_method(self):
            if self.parent:
                self.properties["GroupId"] = self.parent.parent.reference
            return f(self)
        return transformed_method

    @capture_method
    def capture(self):
        self.is_valid = True


class AwsSecurityGroupIngress(AwsSecurityGroupRule):
    def __init__(self, environment, physical_id):
        super().__init__(environment, "AWS::EC2::SecurityGroupIngress", physical_id)


class AwsSecurityGroupEgress(AwsSecurityGroupRule):
    def __init__(self, environment, physical_id):
        super().__init__(environment, "AWS::EC2::SecurityGroupEgress", physical_id)
