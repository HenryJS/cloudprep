from cloudprep.aws.elements.AwsElement import AwsElement


class AwsWaitConditionHandle(AwsElement):
    def __init__(self, environment, physical_id, source_json=None):
        super().__init__("AWS::EC2::AwsWaitCondition", environment, physical_id, source_json)

    @AwsElement.capture_method
    def capture(self):
        self.make_valid()
