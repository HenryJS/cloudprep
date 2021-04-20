import boto3

from .RouteTarget import RouteTarget


class AwsVPCEndpoint(RouteTarget):
    def __init__(self, environment, physical_id, route_table):
        super().__init__("AWS::EC2::VPCEndpoint", environment, physical_id, route_table)
        self._tags = None;

    def local_capture(self):
        ec2 = boto3.client("ec2")
        source_json = ec2.describe_vpc_endpoints(VpcEndpointIds=[self._physical_id])["VpcEndpoints"][0]
        self.set_defaults({
            "PolicyDocument": "{\"Version\":\"2008-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":\"*\",\"Resource\":\"*\"}]}",
            "PrivateDnsEnabled": False,
            "VpcEndpointType": "Gateway"
        })

        self.copy_if_exists("PrivateDnsEnabled", source_json)
        self.copy_if_exists("VpcEndpointType", source_json)

        my_region = boto3.session.Session().region_name
        self._element["ServiceName"] = {
            "Fn::Sub": source_json["ServiceName"].replace(my_region, "${AWS::Region}")
        }

        if "SubnetIds" in source_json:
            self._map_with_references("AWS::EC2::Subnet", source_json["SubnetIds"], "SubnetIds")

        if "RouteTableIds" in source_json:
            self._map_with_references("AWS::EC2::RouteTable", source_json["RouteTableIds"], "RouteTableIds")

        if "Groups" in source_json:
            self._map_with_references("AWS::EC2::SecurityGroup", [ x["GroupId"] for x in source_json["Groups"]], "SecurityGroupIds")

        self._element["VpcId"] = self._route_table.get_vpc().make_reference()
        self.make_valid()

    def _map_with_references(self, aws_type, source_array, local_key):
        if len(source_array) == 0:
            return

        self._element[local_key] = []
        for entry in source_array:
            print("")
            self._element[local_key].append({"Ref": self.calculate_logical_id(aws_type, entry)})