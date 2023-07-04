import boto3
from ..AwsARN import AwsARN
from .AwsStage import AwsStage
from .AwsResource import AwsResource
from .AwsUsagePlan import AwsUsagePlan
from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet


class AwsRestApi(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::ApiGateway::RestApi", physical_id, **kwargs)
        self.set_defaults({
            "ApiKeySourceType": "HEADER",
            "BinaryMediaTypes": [],
            "Description": "",
            "DisableExecuteApiEndpoint": False,
            "EndpointConfiguration": {
                "Types": [
                    "EDGE"
                ]
            },
            "FailOnWarnings": False,
            "MinimumCompressionSize": 0
        })
        self._methods = []
        self._tags = TagSet()

    @AwsElement.capture_method
    def capture(self):
        api_gateway = boto3.client("apigateway")
        if self._source_data is None:
            source_data = api_gateway.get_rest_api(restApiId=self.physical_id)
        else:
            source_data = self._source_data
            self._source_data = None

        self.copy_if_exists("ApiKeySourceType", source_data)
        self.copy_if_exists("BinaryMediaTypes", source_data)
        # "Body" # no OpenAPI
        # "BodyS3Location" # no OpenAPI
        # "CloneFrom": ignoring - by definition, we're not cloning.
        self.copy_if_exists("Description", source_data)
        self.copy_if_exists("DisableExecuteApiEndpoint", source_data)

        if "endpointConfiguration" in source_data:
            endpoint_configuration = {}
            if "types" in source_data["endpointConfiguration"]:
                endpoint_configuration["Types"] = source_data["endpointConfiguration"]["types"]
            if "vpcEndpointIds" in source_data["endpointConfiguration"]:
                raise NotImplementedError("TODO: Cannot build private API Gateways yet")
            self._element["EndpointConfiguration"] = endpoint_configuration

        self.copy_if_exists("FailOnWarnings", source_data)
        self.copy_if_exists("MinimumCompressionSize", source_data)
        # TODO: "Mode" : String,
        self.copy_if_exists("Name", source_data, "name")
        # TODO: "Parameters" : {Key: Value, ...},
        # TODO: "Policy" : Json,
        self._tags.from_api_result(source_data)

        #
        # Capture API Resources
        #
        resources = api_gateway.get_resources(restApiId=self.physical_id)["items"]

        root_element = next(filter(lambda x: x["path"] == "/", resources), None)
        if root_element is None:
            raise "Error: Couldn't find a root element."
        root_element_id = root_element["id"]

        for resource in filter(lambda x: x["path"] != "/", resources):
            self._environment.add_to_todo(
                AwsResource(
                    self._environment,
                    resource["id"],
                    parent=self,
                    source_data=resource,
                    root_element_id=root_element_id
                )
            )

        #
        # Capture API Stages & Deploy them.
        #
        stages = api_gateway.get_stages(restApiId=self.physical_id)
        n = 1
        for stage in stages["item"]:
            self._environment.add_to_todo(
                AwsStage(
                    self._environment,
                    self.logical_id + "Stage" + stage["stageName"],
                    source_data=stage,
                    parent=self
                )
            )

        # Capture Usage Plans
        usage_plans = list(filter(
            AwsRestApi.usage_plan_filter(self.physical_id),
            api_gateway.get_usage_plans()["items"]
        ))
        for plan in usage_plans:
            self._environment.add_to_todo(AwsUsagePlan(self._environment, plan["id"], source_data=plan, parent=self))
        self.is_valid = True


    @staticmethod
    def usage_plan_filter(target):
        def filter_func(plan):
            for stage in plan["apiStages"]:
                if stage["apiId"] == target:
                    return True
        return filter_func

    def add_method(self, method):
        self._methods.append(method)

    def wrap_call(self, call):
        try:
            result = call()
        except Exception:
            return None
        return result
