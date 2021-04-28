from ..AwsElement import AwsElement
from ..TagSet import TagSet


class AwsNetworkAcl(AwsElement):
    def __init__(self, environment, physical_id, vpc, source_json=None):
        super().__init__("AWS::EC2::NetworkAcl", environment, physical_id, source_json)
        self.set_defaults({})
        self._tags = TagSet({"CreatedBy": "CloudPrep"})
        self._vpc = vpc
        self._has_associations = False

    @AwsElement.capture_method
    def capture(self):
        if self._source_json is None:
            source_json = None
            pass
        else:
            source_json = self._source_json
            self._source_json = None

        self._element["VpcId"] = self._vpc.make_reference()
        self._tags.from_api_result(source_json)

        n = 0
        for entry in source_json["Entries"]:
            nacl_entry = AwsNetworkAclEntry(self._environment, self._logical_id + "-entry"+str(n), self, entry)
            self._environment.add_to_todo(nacl_entry)
            n = n + 1

        n = 0
        for association in source_json["Associations"]:
            # (self, environment, physical_id, nacl, assoc):
            assoc = AwsSubnetNaclAssociation(
                self._environment,
                association["NetworkAclAssociationId"],
                self,
                association
            )
            self._environment.add_to_todo(assoc)
            self._has_associations = True
            n = n + 1

    @AwsElement.finalise_method
    def finalise(self):
        if self._has_associations:
            self.make_valid()


class AwsNetworkAclEntry(AwsElement):
    def __init__(self, environment, physical_id, nacl, source_json=None):
        super().__init__("AWS::EC2::NetworkAclEntry", environment, physical_id, source_json)
        self.set_defaults({})
        self._nacl = nacl

    @AwsElement.capture_method
    def capture(self):
        source_json = self._source_json
        self._source_json = None

        # If we're the DEFAULT DENY then just return because there's already one there
        if source_json["RuleNumber"] == 32767:
            return

        self.copy_if_exists("CidrBlock", source_json)
        self.copy_if_exists("Egress", source_json)
        self.copy_if_exists("Ipv6CidrBlock", source_json)
        self.copy_if_exists("PortRange", source_json)
        self.copy_if_exists("Protocol", source_json)
        self.copy_if_exists("RuleAction", source_json)
        self.copy_if_exists("RuleNumber", source_json)

        if "IcmpTypeCode" in source_json:
            self._element["Icmp"] = source_json["IcmpTypeCode"]

        self._element["NetworkAclId"] = self._nacl.make_reference()
        self.make_valid()


class AwsSubnetNaclAssociation(AwsElement):
    def __init__(self, environment, physical_id, nacl, assoc):
        super().__init__("AWS::EC2::SubnetNetworkAclAssociation", environment, physical_id, assoc)
        self._nacl = nacl

    @AwsElement.capture_method
    def capture(self):
        self._element["NetworkAclId"] = self._nacl.make_reference()

        self._element["SubnetId"] = \
            self._environment.find_by_physical_id(self._source_json["SubnetId"]).make_reference()
        self.make_valid()

