from cloudprep.aws.elements.AwsElement import AwsElement


class AwsWaitConditionHandle(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::EC2::AwsWaitCondition", physical_id, **kwargs)

    @AwsElement.capture_method
    def capture(self):
        self.is_valid = True
