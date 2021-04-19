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
        # {
        #     "Type": "AWS::EC2::VPCEndpoint",
        #     "Properties": {
        #         "RouteTableIds": [String, ...],
        #         "SecurityGroupIds": [String, ...],
        #     }
        # }

        # TODO: Not do this if the policy is default.
        self.copy_if_exists("PolicyDocument", source_json)
        self.copy_if_exists("PrivateDnsEnabled", source_json)
        self.copy_if_exists("VpcEndpointType", source_json)

        # TODO: Translate this between regions
        my_region = boto3.session.Session().region_name
        self._element["ServiceName"] = {
            "Fn::Sub": source_json["ServiceName"].replace(my_region, "${AWS::Region}")
        }

        # for key in ["SubnetIds", "RouteTableIds"]:
        #     if len(source_json[key]) > 0:
        #         self._element[key] = source_json[key]

        if len(source_json["Groups"]) > 0:
            self._element["SecurityGroupIds"] = source_json["Groups"]

        self._element["VpcId"] = self._route_table.get_vpc().make_reference()

        self.make_valid()
