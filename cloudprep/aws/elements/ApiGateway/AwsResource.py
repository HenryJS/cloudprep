from cloudprep.aws.elements.AwsElement import AwsElement
from .AwsMethod import AwsMethod


class AwsResource(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::ApiGateway::Resource", physical_id, **kwargs)
        self.set_defaults({})
        self._root_id = kwargs["root_element_id"]

    @AwsElement.capture_method
    def capture(self):
        if self._source_data is None:
            source_data = None
            pass
        else:
            source_data = self._source_data
            self._source_data = None

        self._element["RestApiId"] = self.make_reference(self._parent.logical_id)
        self._element["PathPart"] = source_data["pathPart"]

        if source_data["parentId"] == self._root_id:
            self._element["ParentId"] = self.make_getatt(
                "RootResourceId", self._parent.logical_id
            )
        else:
            self._element["ParentId"] = self.make_reference(physical_id=source_data["parentId"])

        #
        # Capture the Methods associated with this Resource
        #
        if "resourceMethods" in source_data:
            for method in source_data["resourceMethods"].keys():
                self._environment.add_to_todo(AwsMethod(
                    self._environment,
                    parent=self._parent,
                    resource_id=source_data["id"],
                    http_method=method
                ))

        self.is_valid = True

