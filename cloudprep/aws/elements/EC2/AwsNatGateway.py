import boto3

from .RouteTarget import RouteTarget
from .AwsEIP import AwsEIP


class AwsNatGateway(RouteTarget):
    def __init__(self, environment, physical_id, route):
        super().__init__("AWS::EC2::NatGateway", environment, physical_id, route)

    def local_capture(self):
        ec2 = boto3.client("ec2")
        if self._source_json is None:
            source_json = ec2.describe_nat_gateways(NatGatewayIds=[self._physical_id])["NatGateways"][0]
        else:
            source_json = self._source_json
            self._source_json = None

        if source_json["State"] not in ["Pending", "Available"]:
            return

        self._element["SubnetId"] = self._environment.find_by_physical_id(source_json["SubnetId"]).make_reference()

        if "Tags" in source_json:
            self._tags.from_api_result(source_json["Tags"])

        eip_allocation = source_json["NatGatewayAddresses"][0]
        eip = AwsEIP(self._environment, eip_allocation["AllocationId"], eip_allocation)
        self._environment.add_to_todo(eip)

        self._element["AllocationId"] = eip.make_getatt("AllocationId")

        self.make_valid()
