from .RouteTarget import RouteTarget


class AwsEgressOnlyInternetGateway(RouteTarget):
    def __init__(self, environment, physical_id, route_table):
        super().__init__("AWS::EC2::EgressOnlyInternetGateway", environment, physical_id, route_table)

    def local_capture(self):
        self._element["VpcId"] = self._attached_vpc.make_reference()
        self.make_valid()
