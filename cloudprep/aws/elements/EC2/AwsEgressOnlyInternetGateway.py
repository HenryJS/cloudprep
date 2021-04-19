from cloudprep.aws.elements.AwsElement import AwsElement


class AwsEgressOnlyInternetGateway(AwsElement):
    def __init__(self, environment, physical_id, vpc, source_json=None):
        super().__init__("AWS::EC2::EgressOnlyInternetGateway", environment, physical_id, source_json)
        self._attached_vpc = vpc

    def local_capture(self):
        self._element["VpcId"] = self._attached_vpc.make_reference()

        self.make_valid()
