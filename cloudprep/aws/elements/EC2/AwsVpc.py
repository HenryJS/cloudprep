import boto3

from ..AwsElement import AwsElement
from ..TagSet import TagSet
from .AwsSubnet import AwsSubnet
from .AwsSecurityGroup import AwsSecurityGroup
from .AwsRouteTable import AwsRouteTable
from .AwsNetworkAcl import AwsNetworkAcl
from .AwsVpcEndpoint import AwsVPCEndpoint


class AwsVpc(AwsElement):
    def __init__(self, environment, physical_id):
        super().__init__("AWS::EC2::VPC", environment, physical_id)
        self.set_defaults({
            "EnableDnsHostnames": False,
            "EnableDnsSupport": True,
            "InstanceTenancy": "default"
        })
        self._tags = TagSet({"CreatedBy": "CloudPrep"})
        self._main_route_table = None
        self._subnets = []

    @AwsElement.capture_method
    def capture(self):
        ec2 = boto3.client("ec2")
        source_json = ec2.describe_vpcs(VpcIds=[self._physical_id])["Vpcs"][0]

        self.copy_if_exists("CidrBlock", source_json)
        self.copy_if_exists("InstanceTenancy", source_json)
        if "Tags" in source_json:
            self._tags.from_api_result(source_json["Tags"])

        for attrib in ["enableDnsSupport", "enableDnsHostnames"]:
            attrib_query = ec2.describe_vpc_attribute(
                VpcId=self._physical_id,
                Attribute=attrib
            )
            attrib_uc = attrib[0].upper() + attrib[1:]
            if not self.is_default(attrib_uc, attrib_query[attrib_uc]["Value"]):
                self._element[attrib_uc] = attrib_query[attrib_uc]["Value"]

        # Create a filter for use in subsequent calls.
        vpc_filter = [{"Name": "vpc-id", "Values": [self._physical_id]}]
        # att_vpc_filter = [{"Name": "attachment.vpc-id", "Values": [self._physical_id]}]

        for results_page in ec2.get_paginator("describe_subnets").paginate(Filters=vpc_filter):
            for net in results_page["Subnets"]:
                subnet = AwsSubnet(self._environment, net["SubnetId"], net)
                self._environment.add_to_todo(subnet)
                self._subnets.append(subnet)

        for results_page in ec2.get_paginator("describe_network_acls").paginate(Filters=vpc_filter):
            for nacl in results_page["NetworkAcls"]:
                network_acl = AwsNetworkAcl(self._environment, nacl["NetworkAclId"], self, nacl)
                self._environment.add_to_todo(network_acl)

        for results_page in ec2.get_paginator("describe_security_groups").paginate(Filters=vpc_filter):
            for syg in results_page["SecurityGroups"]:
                self._environment.add_to_todo(
                    AwsSecurityGroup(
                        self._environment,
                        syg["GroupId"],
                        syg
                    ))

        for rt in ec2.describe_route_tables(Filters=vpc_filter)["RouteTables"]:
            route_table = AwsRouteTable(self._environment, rt["RouteTableId"], rt, self)
            self._environment.add_to_todo(route_table)

        vpce_filter = vpc_filter
        vpce_filter.append({"Name": "vpc-endpoint-type", "Values": ["Interface"]})
        for results_page in ec2.get_paginator("describe_vpc_endpoints").paginate(Filters=vpce_filter):
            for vpce in results_page["VpcEndpoints"]:
                vpc_endpoint = AwsVPCEndpoint(self._environment, vpce["VpcEndpointId"], self)
                self._environment.add_to_todo(vpc_endpoint)

        self.make_valid()

    def set_main_route_table(self, main_rtb):
        self._main_route_table = main_rtb

    def get_vpc(self):
        """ This is an nasty hack """
        return self

    @AwsElement.finalise_method
    def finalise(self):
        more_work = False
        # To finalise, scan subnets and add the main table to any that don't already have it.
        for subnet in self._subnets:
            if not subnet.has_route_table():
                # print("Found a subnet associated with main route table. Manually associating", file=sys.stderr)
                subnet.set_route_table(self._main_route_table)
                self._main_route_table.associate_with_subnet(subnet.physical_id)
                more_work = True

        return more_work

