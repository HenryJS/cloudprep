from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet


class AwsWaitConditionHandle(AwsElement):
    def __init__(self, environment, physical_id, source_json=None):
        super().__init__("AWS::EC2::AwsWaitCondition", environment, physical_id, source_json)

    def local_capture(self):
        self.make_valid()