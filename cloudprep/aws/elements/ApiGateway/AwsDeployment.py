from cloudprep.aws.elements.AwsElement import AwsElement

class AwsDeployment(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::ApiGateway::Deployment", physical_id, **kwargs)
        self.set_defaults({})

    @AwsElement.capture_method
    def capture(self):
        if self._source_data is None:
            source_data = None
            pass
        else:
            source_data = self._source_data
            self._source_data = None
        #         "DeploymentCanarySettings": DeploymentCanarySettings,
        #         "StageDescription": StageDescription,
        self._element["RestApiId"] = self.make_reference(self._parent._parent.logical_id)
        # self._element["StageName"] = self.make_reference(self._parent.logical_id)
        self.copy_if_exists("Description", source_data)

        self.is_valid = True
        return source_data
