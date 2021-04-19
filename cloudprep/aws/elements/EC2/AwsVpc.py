import boto3

from cloudprep.aws.elements.AwsElement import AwsElement
from .AwsSubnet import AwsSubnet
from .AwsSecurityGroup import AwsSecurityGroup
from .AwsInternetGateway import AwsInternetGateway
from .AwsRouteTable import AwsRouteTable
from cloudprep.aws.elements.TagSet import TagSet


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
        vpc_id_filter = [{"Name": "vpc-id", "Values": [self._physical_id]}]

        for net in ec2.describe_subnets(Filters=vpc_id_filter)["Subnets"]:
            subnet = AwsSubnet(self._environment, net["SubnetId"], net)
            self._environment.add_to_todo(subnet)
            self._subnets.append(subnet)

        for syg in ec2.describe_security_groups(Filters=vpc_id_filter)["SecurityGroups"]:
            if syg["GroupName"] != "default":
                self._environment.add_to_todo(
                    AwsSecurityGroup(
                        self._environment,
                        syg["GroupId"],
                        syg
                    ))

        for igw in ec2.describe_internet_gateways(
                Filters=[{"Name": "attachment.vpc-id", "Values": [self._physical_id]}]
        )["InternetGateways"]:
            aws_igw = AwsInternetGateway(self._environment, igw["InternetGatewayId"], self, igw)
            self._environment.add_to_todo(aws_igw)

        for rt in ec2.describe_route_tables(Filters=vpc_id_filter)["RouteTables"]:
            route_table = AwsRouteTable(self._environment, rt["RouteTableId"], rt, self)
            self._environment.add_to_todo(route_table)

        self.make_valid()

    def set_main_route_table(self, main_rtb):
        self._main_route_table = main_rtb

    def finalise(self):
        more_work = False
        # To finalise, scan subnets and add the main table to any that don't already have it.
        for subnet in self._subnets:
            if not subnet.has_route_table():
                # print("Found a subnet associated with main route table. Manually associating", file=sys.stderr)
                subnet.set_route_table(self._main_route_table)
                self._main_route_table.associate_with_subnet(subnet.get_physical_id())
                more_work = True

        return more_work

