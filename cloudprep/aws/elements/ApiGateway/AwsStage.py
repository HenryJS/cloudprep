import boto3
from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet
from .AwsDeployment import AwsDeployment


class AwsStage(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::ApiGateway::Stage", physical_id, **kwargs)
        self.set_defaults({
            "TracingEnabled": False
        })
        self._tags = TagSet({"CreatedBy": "CloudPrep"})

    @AwsElement.capture_method
    def capture(self):
        self._element["PhysicalId"] = self._physical_id
        api_gateway = boto3.client("apigateway")

        if self._source_data is None:
            source_data = None
            pass
        else:
            source_data = self._source_data
            self._source_data = None

        #{
        #   "Type" : "AWS::ApiGateway::Stage",
        #   "Properties" : {
        #       "AccessLogSetting" : AccessLogSetting,
        self.copy_if_exists("CacheClusterEnabled", source_data, "cacheClusterEnabled")
        self.copy_if_exists("CacheClusterSize", source_data, "cacheClusterSize")
        self.copy_if_exists("Description", source_data, "description")
        self.copy_if_exists("StageName", source_data, "stageName")
        self.copy_if_exists("TracingEnabled", source_data, "tracingEnabled")

        # TODO: "CanarySetting" : CanarySetting,
        # TODO: "ClientCertificateId" : String,

        deployment = self._environment.find_by_physical_id(source_data["deploymentId"])
        if deployment is None:
            deployment = AwsDeployment(self._environment, physical_id=source_data["deploymentId"], parent=self._parent)
            self._environment.add_to_todo(deployment)
        self._element["DeploymentId"] = deployment.logical_id

        # TODO: "DocumentationVersion" : String,
        # TODO: "MethodSettings" : [ MethodSetting, ... ],

        self._element["RestApiId"] = self._parent.logical_id

        if "tags" in source_data:
            self._tags.from_api_result(source_data)

        # TODO: "Variables" : {Key: Value, ...}

        self.is_valid = True
