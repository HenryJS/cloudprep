import sys

from cloudprep.aws.elements.AwsElement import AwsElement

from .RouteTargetBuilder import RouteTargetBuilder


class AwsRoute(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::EC2::Route", physical_id, **kwargs)
        self._route_table = kwargs["route_table"]

    @AwsElement.capture_method
    def capture(self):
        # ec2 = boto3.client("ec2")
        # self._source_data = None
        # if self._source_data is None:
        #     source_data = ec2.describe_route_tables(RouteTableIds=[self._physical_id])["RouteTables"][0]
        # else:
        source_data = self._source_data
        self._source_data = None

        self._element["RouteTableId"] = self._route_table.make_reference()
        self.copy_if_exists("DestinationCidrBlock", source_data)
        self.copy_if_exists("DestinationIpv6CidrBlock", source_data)
        if source_data["State"] == "blackhole":
            print("-- Route skipped (blackholing)", file=sys.stderr)
            return

        for target_id_key in [
            "CarrierGatewayId",
            "EgressOnlyInternetGatewayId",
            "GatewayId",
            "InstanceId",
            "LocalGatewayId",
            "NatGatewayId",
            "NetworkInterfaceId",
            "TransitGatewayId",
            "VpcEndpointId",
            "VpcPeeringConnectionId"
        ]:
            if target_id_key in source_data:
                assoc_prefix = source_data[target_id_key].split("-")[0]
                kwargs = { "environment": self._environment, "physical_id": source_data[target_id_key], "route": self}
                target = RouteTargetBuilder.find_route_target(assoc_prefix, **kwargs )

                if target is None:
                    return

                self._environment.add_to_todo(target)
                self._element[target_id_key] = target.make_reference()

        self.is_valid = True
        # TODO:
        #       "CarrierGatewayId" : String,
        #       "InstanceId" : String,
        #       "LocalGatewayId" : String,
        #       "NetworkInterfaceId" : String,
        #       "VpcEndpointId" : String,
        #       "VpcPeeringConnectionId" : String

    @property
    def route_table(self):
        return self._route_table

    @AwsElement.finalise_method
    def finalise(self):
        if "DestinationCidrBlock" not in self._element and "DestinationIpv6CidrBlock" not in self._element:
            self.is_valid = False

