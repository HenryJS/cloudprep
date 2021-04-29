import boto3

from .RouteTarget import RouteTarget


class AwsVPCEndpoint(RouteTarget):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__("AWS::EC2::VPCEndpoint", environment, physical_id, **kwargs)
        self._tags = None

    @RouteTarget.capture_method
    def capture(self):
        ec2 = boto3.client("ec2")
        source_data = ec2.describe_vpc_endpoints(VpcEndpointIds=[self._physical_id])["VpcEndpoints"][0]
        # noinspection PyPep8
        self.set_defaults({
            "PolicyDocument": "{\"Version\":\"2008-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":\"*\",\"Resource\":\"*\"}]}",
            "PrivateDnsEnabled": False,
            "VpcEndpointType": "Gateway"
        })

        self.copy_if_exists("PrivateDnsEnabled", source_data)
        self.copy_if_exists("VpcEndpointType", source_data)

        my_region = boto3.session.Session().region_name
        self._element["ServiceName"] = {
            "Fn::Sub": source_data["ServiceName"].replace(my_region, "${AWS::Region}")
        }

        if "SubnetIds" in source_data:
            self._map_with_references(source_data["SubnetIds"], "SubnetIds")

        if "RouteTableIds" in source_data:
            self._map_with_references(source_data["RouteTableIds"], "RouteTableIds")

        if "Groups" in source_data:
            self._map_with_references([x["GroupId"] for x in source_data["Groups"]], "SecurityGroupIds")

        self.refer_if_exists("VpcId", source_data)
        self.is_valid = True

    def _map_with_references(self, source_array, local_key):
        if len(source_array) == 0:
            return

        self._element[local_key] = []
        for entry in source_array:
            print("")
            self._element[local_key].append({"Ref": self.calculate_logical_id(entry)})
