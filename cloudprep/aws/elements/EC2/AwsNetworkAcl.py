import sys

from ..AwsElement import AwsElement
from ..TagSet import TagSet


class AwsNetworkAcl(AwsElement):
    def __init__(self, environment, physical_id, vpc, **kwargs):
        super().__init__(environment, "AWS::EC2::NetworkAcl", physical_id, **kwargs)
        self.set_defaults({})
        self._tags = TagSet({"CreatedBy": "CloudPrep"})
        self._vpc = vpc
        self._has_associations = False
        self._rules = []

    @AwsElement.capture_method
    def capture(self):
        if self._source_data is None:
            source_data = None
            pass
        else:
            source_data = self._source_data
            self._source_data = None

        self._element["VpcId"] = self._vpc.make_reference()
        self._tags.from_api_result(source_data)

        n = 0
        for entry in source_data["Entries"]:
            nacl_entry = AwsNetworkAclEntry(self._environment, self._logical_id + "-entry"+str(n), nacl=self, source_data=entry)
            self._environment.add_to_todo(nacl_entry)
            self._rules.append(nacl_entry)
            n = n + 1

        n = 0
        for association in source_data["Associations"]:
            # (self, environment, physical_id, nacl, assoc):
            assoc = AwsSubnetNaclAssociation(
                self._environment,
                association["NetworkAclAssociationId"],
                nacl=self,
                source_data=association
            )
            self._environment.add_to_todo(assoc)
            self._has_associations = True
            n = n + 1

        self.is_valid = True

    @AwsElement.finalise_method
    def finalise(self):
        if not self._has_associations:
            self.is_valid = False

            for rule in self._rules:
                rule.is_valid = False


class AwsNetworkAclEntry(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::EC2::NetworkAclEntry", physical_id, **kwargs)
        self.set_defaults({})
        self._nacl = kwargs["nacl"]

    @AwsElement.capture_method
    def capture(self):
        source_data = self._source_data
        self._source_data = None

        # If we're the DEFAULT DENY then just return because there's already one there
        if source_data["RuleNumber"] == 32767:
            return

        self.copy_if_exists("CidrBlock", source_data)
        self.copy_if_exists("Egress", source_data)
        self.copy_if_exists("Ipv6CidrBlock", source_data)
        self.copy_if_exists("PortRange", source_data)
        self.copy_if_exists("Protocol", source_data)
        self.copy_if_exists("RuleAction", source_data)
        self.copy_if_exists("RuleNumber", source_data)

        if "IcmpTypeCode" in source_data:
            self._element["Icmp"] = source_data["IcmpTypeCode"]

        self._element["NetworkAclId"] = self._nacl.make_reference()
        self.is_valid = True


class AwsSubnetNaclAssociation(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::EC2::SubnetNetworkAclAssociation", physical_id, **kwargs)
        self._nacl = kwargs["nacl"]

    @AwsElement.capture_method
    def capture(self):
        self._element["NetworkAclId"] = self._nacl.make_reference()

        self._element["SubnetId"] = \
            self._environment.find_by_physical_id(self._source_data["SubnetId"]).make_reference()
        self.is_valid = True

