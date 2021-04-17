import boto3

from .AwsElement import AwsElement

class SimpleElement(AwsElement):
    def __init__(self,environment, phyiscalId):
        super().__init__( "AWS::EC2::SimpleElement", environment)
        self.setDefaults( { "EnableDnsHostnames": False,
                             "EnableDnsSupport": True
                             } )
        self._physical_id = phyiscalId

    def capture(self):
        self._element["PhysicalId"] = self._physical_id