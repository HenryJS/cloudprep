import boto3

from .RouteTarget import RouteTarget
from .AwsEIP import AwsEIP
import sys


class AwsNatGateway(RouteTarget):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__("AWS::EC2::NatGateway", environment, physical_id, **kwargs)

    @RouteTarget.capture_method
    def capture(self):
        ec2 = boto3.client("ec2")
        if self._source_data is None:
            source_data = ec2.describe_nat_gateways(NatGatewayIds=[self._physical_id])["NatGateways"][0]
        else:
            source_data = self._source_data
            self._source_data = None

        if source_data["State"] not in ["pending", "available"]:
            return

        self._element["SubnetId"] = self._environment.find_by_physical_id(source_data["SubnetId"]).make_reference()

        if "Tags" in source_data:
            self._tags.from_api_result(source_data["Tags"])

        eip_allocation = source_data["NatGatewayAddresses"][0]
        eip = AwsEIP(self._environment, eip_allocation["AllocationId"], source_data=eip_allocation)
        self._environment.add_to_todo(eip)

        self._element["AllocationId"] = eip.make_getatt("AllocationId")

        self.is_valid = True
