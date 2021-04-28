from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet


class SimpleElement(AwsElement):
    def __init__(self, environment, physical_id, source_json=None):
        super().__init__("AWS::EC2::SimpleElement", environment, physical_id, source_json)
        self.set_defaults({})
        self._tags = TagSet({"CreatedBy": "CloudPrep"})

    def local_capture(self):
        self._element["PhysicalId"] = self._physical_id

        if self._source_json is None:
            source_json = None
            pass
        else:
            source_json = self._source_json
            self._source_json = None

        return source_json
