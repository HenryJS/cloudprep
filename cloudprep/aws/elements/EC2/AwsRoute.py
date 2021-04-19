import sys

from cloudprep.aws.elements.AwsElement import AwsElement


TARGET_ASSOC = {
    "GatewayId": {
        "igw": "AWS::EC2::InternetGateway",
        "loc": None
    },
    "NatGatewayId": {
        "nat": "AWS::EC2::NatGateway"
    },
    "EgressOnlyInternetGatewayId": {
        "eig": "AWS::EC2::EgressOnlyInternetGateway"
    }
}


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
                if target_id_key not in TARGET_ASSOC:
                    raise NotImplementedError(target_id_key + " is not yet a supported Route Target")

                assoc_prefix = source_json[target_id_key][0:3]
                if assoc_prefix not in TARGET_ASSOC[target_id_key]:
                    raise NotImplementedError(assoc_prefix + " is not yet a supported " + target_id_key)
                target_type = TARGET_ASSOC[target_id_key][assoc_prefix]

                if target_type is None:
                    return
                else:
                    target_id_value = self._environment.find_by_physical_id(source_json[target_id_key]).make_reference()
                    # target_id_value = {"Ref": self.calculate_logical_id(target_type, source_json[target_id_key])}

                self._element[target_id_key] = target_id_value

        self.make_valid()
        # TODO:
        #       "CarrierGatewayId" : String,
        #       "InstanceId" : String,
        #       "LocalGatewayId" : String,
        #       "NetworkInterfaceId" : String,
        #       "TransitGatewayId" : String,
        #       "VpcEndpointId" : String,
        #       "VpcPeeringConnectionId" : String
