from .RouteTarget import RouteTarget


class AwsEgressOnlyInternetGateway(RouteTarget):
    def __init__(self, environment, physical_id, route_table):
        super().__init__("AWS::EC2::EgressOnlyInternetGateway", environment, physical_id, route_table)

    @RouteTarget.capture_method
    def capture(self):
        self._element["VpcId"] = self._route.get_route_table().get_vpc().make_reference()
        self.is_valid = True
