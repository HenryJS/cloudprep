from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet


class AwsLambdaFunction(AwsElement):
    def __init__(self, environment, physical_id, source_json=None):
        super().__init__(environment, "AWS::Lambda::Function", physical_id, source_json)
        self.set_defaults({})
        self._tags = TagSet({"CreatedBy": "CloudPrep"})

    @AwsElement.capture_method
    def capture(self):
        self._element["PhysicalId"] = self._physical_id

        if self._source_json is None:
            source_json = None
            pass
        else:
            source_json = self._source_json
            self._source_json = None

        self.is_valid = True
        return source_json
