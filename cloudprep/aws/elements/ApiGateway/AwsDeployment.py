from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet


class AwsDeployment(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::ApiGateway::Deployment", physical_id, **kwargs)
        self.set_defaults({})
        self._tags = TagSet()

    @AwsElement.capture_method
    def capture(self):
        self._element["PhysicalId"] = self._physical_id

        if self._source_data is None:
            source_data = None
            pass
        else:
            source_data = self._source_data
            self._source_data = None

        self._element["RestApiId"] = self._parent.logical_id

        self.is_valid = True
        return source_data
