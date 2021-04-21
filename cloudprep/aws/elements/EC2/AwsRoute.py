import sys

from cloudprep.aws.elements.AwsElement import AwsElement

from .RouteTargetBuilder import RouteTargetBuilder


class AwsRoute(AwsElement):
    def __init__(self, environment, physical_id, source_json=None, route_table=None):
        super().__init__("AWS::EC2::Route", environment, physical_id, source_json)
        self._route_table = route_table

    def local_capture(self):
        # ec2 = boto3.client("ec2")
        # self.set_source_json(None)
        # if self._source_json is None:
        #     source_json = ec2.describe_route_tables(RouteTableIds=[self._physical_id])["RouteTables"][0]
        # else:
        source_json = self._source_json
        self.set_source_json(None)

        self._element["RouteTableId"] = self._route_table.make_reference()
        self.copy_if_exists("DestinationCidrBlock", source_json)
        self.copy_if_exists("DestinationIpv6CidrBlock", source_json)
        if source_json["State"] == "blackhole":
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
            if target_id_key in source_json:
                assoc_prefix = source_json[target_id_key].split("-")[0]
                target_class = RouteTargetBuilder.find_route_target(assoc_prefix)

                if target_class is None:
                    return

                target = target_class(
                    self._environment,
                    source_json[target_id_key],
                    self
                )
                self._environment.add_to_todo(target)
                self._element[target_id_key] = target.make_reference()

        self.make_valid()
        # TODO:
        #       "CarrierGatewayId" : String,
        #       "InstanceId" : String,
        #       "LocalGatewayId" : String,
        #       "NetworkInterfaceId" : String,
        #       "VpcEndpointId" : String,
        #       "VpcPeeringConnectionId" : String

    def get_route_table(self):
        return self._route_table

    def local_finalise(self):
        if "DestinationCidrBlock" not in self._element and "DestinationIpv6CidrBlock" not in self._element:
            self.make_valid(False)