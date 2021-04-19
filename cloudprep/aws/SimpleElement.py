from cloudprep.aws.elements.AwsElement import AwsElement


class SimpleElement(AwsElement):
    def __init__(self, environment, physical_id):
        super().__init__("AWS::EC2::SimpleElement", environment, physical_id)
        self.set_defaults(
            {
                "EnableDnsHostnames": False,
                "EnableDnsSupport": True
            }
        )

    def capture(self):
        self._element["PhysicalId"] = self._physical_id
