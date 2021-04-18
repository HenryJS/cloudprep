import boto3

from cloudprep.aws.elements.AwsElement import AwsElement


class AwsVpcGatewayAttachment(AwsElement):
    def __init__(self, environment, physical_id, vpc):
        super().__init__("AWS::EC2::VPCGatewayAttachment", environment, physical_id)
        self._vpc = vpc
        self.set_vpn_gateway(None)
        self.set_internet_gateway(None)

    def set_internet_gateway(self, internet_gateway):
        self._internet_gateway = internet_gateway

    def set_vpn_gateway(self, vpn_gateway):
        self._vpn_gateway = vpn_gateway

    def capture(self):
        self._element["VpcId"] = {"Ref": self._vpc.get_logical_id()}

        if self._internet_gateway is not None:
            self._element["InternetGatewayId"] = {"Ref": self._internet_gateway.get_logical_id()}

        if self._vpn_gateway is not None:
            self._element["VpnGatewayId"] = {"Ref": self._vpn_gateway.get_logical_id()}

        self.makeValid()

