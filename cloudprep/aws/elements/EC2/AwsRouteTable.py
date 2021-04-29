import boto3

from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet
from .AwsRoute import AwsRoute


class AwsRouteTable(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::EC2::RouteTable", physical_id, **kwargs)
        self._tags = TagSet({"CreatedBy": "CloudPrep"})
        self._vpc = kwargs["vpc"]
        self._has_associations = False
        self._routes = []

    @AwsElement.capture_method
    def capture(self):
        ec2 = boto3.client("ec2")
        self._source_data = None
        if self._source_data is None:
            source_data = ec2.describe_route_tables(RouteTableIds=[self._physical_id])["RouteTables"][0]
        else:
            source_data = self._source_data
            self._source_data = None

        self._element["VpcId"] = self.vpc.make_reference()
        self._tags.from_api_result(source_data)

        # All the subnets!
        for association in source_data["Associations"]:
            # Is this the Main route table?
            if association["Main"]:
                self._vpc.set_main_route_table(self)
                self._tags.add_tag("cloudprep:wasMain", "True")
            else:
                self.associate_with_subnet(association["SubnetId"])

        for i, route in zip(range(len(source_data["Routes"])), source_data["Routes"]):
            rt = AwsRoute(self._environment, self._physical_id + "-route" + str(i), source_data=route, route_table=self)
            self._routes.append(rt)
            self._environment.add_to_todo(rt)

        self.is_valid = True

    @property
    def vpc(self):
        return self._vpc

    def associate_with_subnet(self, subnet_id):
        assoc = AwsSubnetRouteTableAssociation(
            self._environment,
            self._physical_id + "-" + subnet_id,
            self,
            subnet_id
        )
        self._environment.add_to_todo(assoc)
        self._has_associations = True

    @AwsElement.finalise_method
    def finalise(self):
        more_work = False

        # If we have no associations, we might not need to be here =)
        if not self._has_associations and str(self._tags.get_tag("cloudprep:forceCapture")).upper() != "TRUE":
            self.is_valid = False

            for route in self._routes:
                route.is_valid = False

            return

        # Find those that depend on a TGW and add the explicit dependency
        # vpc_id = self.vpc.logical_id
        # for route in self._routes:
        #     if "TransitGatewayId" in route.properties:
        #         tga = VpcAttachmentRegistry.get_attachment(
        #             vpc_logical_id=vpc_id,
        #             subject_logical_id=route.properties["TransitGatewayId"]["Ref"]
        #         )
        #
        #         if tga is None:
        #             # We get here because we have multiple VPCs pointing at a single TGW.  One of those probably
        #             # caused the TGW to be made, but it hasn't yet been linked everywhere.
        #
        #             tgw = self._environment.find_by_logical_id(route.properties["TransitGatewayId"]["Ref"])
        #             tga = AwsTransitGatewayVpcAttachment(self._environment, tgw.physical_id + "attach" + vpc_id, route=route)
        #             print("VPC Logical ID =", vpc_id,file=sys.stderr)
        #             print("TGW Logical ID =", tgw.logical_id,file=sys.stderr)
        #             print("TGA Logical ID =", tga.logical_id,file=sys.stderr)
        #             self._environment.add_to_todo(tga)
        #
        #             VpcAttachmentRegistry.register_attachment(self.vpc, tgw, tga)
        #
        #             more_work = True
        #         else:
        #             route.add_dependency(tga.logical_id)

        return more_work

class AwsSubnetRouteTableAssociation(AwsElement):
    def __init__(self, environment, physical_id, route_table, subnet_id):
        super().__init__(environment, "AWS::EC2::SubnetRouteTableAssociation", physical_id)
        self._route_table = route_table
        self._subnet_id = subnet_id

    @AwsElement.capture_method
    def capture(self):
        if self._subnet_id is not None:
            self._element["RouteTableId"] = self._route_table.make_reference()
            target_subnet = self._environment.find_by_physical_id(self._subnet_id)

            self._element["SubnetId"] = target_subnet.make_reference()
            target_subnet.set_route_table(self._route_table)
            self.is_valid = True
