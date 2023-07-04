import boto3
from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet
from .AwsDeployment import AwsDeployment
from ..AwsARN import AwsARN
from ..Logs.AwsLogGroup import AwsLogGroup

class AwsStage(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::ApiGateway::Stage", physical_id, **kwargs)
        self.set_defaults({
            "TracingEnabled": False
        })
        self._tags = TagSet()

    @AwsElement.capture_method
    def capture(self):
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
        self.copy_if_exists("CacheClusterEnabled", source_data)
        self.copy_if_exists("CacheClusterSize", source_data)
        self.copy_if_exists("Description", source_data)
        self.copy_if_exists("StageName", source_data)
        self.copy_if_exists("TracingEnabled", source_data)

        if "accessLogSettings" in source_data:
            als = {}
            self.copy_if_exists("Format", source_data["accessLogSettings"], destination_data=als)
            if "destinationArn" in source_data["accessLogSettings"]:
                dest_arn = AwsARN(source_data["accessLogSettings"]["destinationArn"])
                if dest_arn.service == "logs":
                    als["DestinationArn"] = dest_arn.text
                    self._environment.add_to_todo(AwsLogGroup(self._environment, dest_arn))
                else:
                    raise NotImplementedError("Unimplemented API Gateway Stage Log Destination: " + dest_arn.text)

        # TODO: "ClientCertificateId" : String,

        if "deploymentId" in source_data:
            deployment_src = api_gateway.get_deployment(
                restApiId=self._parent.logical_id,
                deploymentId=source_data["deploymentId"])
            deployment = AwsDeployment(self._environment,
                                       physical_id=source_data["deploymentId"],
                                       parent=self,
                                       source_data=deployment_src)
            self._element["DeploymentId"] = self.make_reference(deployment.logical_id)
            deployment.add_dependencies(self._parent._methods)
            self._environment.add_to_todo(deployment)

        # # deployment = self._environment.find_by_physical_id(source_data["deploymentId"])
        # # if deployment is None:
        # #     deployment = AwsDeployment(self._environment, physical_id=source_data["deploymentId"], parent=self._parent)
        # #     self._environment.add_to_todo(deployment)
        # self._element["DeploymentId"] = deployment.logical_id

        # TODO: "CanarySetting" : CanarySetting.DeploymentId
        if "canarySettings" in source_data:
            canary = {}
            self.copy_if_exists("PercentTraffic", source_data, destination_data=canary)
            self.copy_if_exists("StageVariableOverrides", source_data, destination_data=canary)
            self.copy_if_exists("UseStageCache", source_data, destination_data=canary)

        # TODO: "DocumentationVersion" : String,
        # TODO: "MethodSettings" : [ MethodSetting, ... ],

        self._element["RestApiId"] = self.make_reference(self._parent.logical_id)

        if "tags" in source_data:
            self._tags.from_api_result(source_data)

        # TODO: "Variables" : {Key: Value, ...}

        self.is_valid = True
