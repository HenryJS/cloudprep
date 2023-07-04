import boto3
from cloudprep.aws.elements.AwsElement import AwsElement
from .AwsUsagePlanKey import AwsUsagePlanKey
from ..TagSet import TagSet
class AwsUsagePlan(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::ApiGateway::UsagePlan", physical_id, **kwargs)
        self.set_defaults({})
        self._tags = TagSet()

    @AwsElement.capture_method
    def capture(self):
        if self._source_data is None:
            source_data = None
            pass
        else:
            source_data = self._source_data
            self._source_data = None

        self.copy_if_exists("Description", source_data)
        self.copy_if_exists("UsagePlanName", source_data, source_key="name")
        if "tags" in source_data:
            self._tags.from_api_result(source_data["tags"])

        if "apiStages" in source_data:
            api_stages = []
            for stage_src in source_data["apiStages"]:
                stage = {}
                # Sanity check
                assert stage_src["apiId"] == self._parent.logical_id
                stage["ApiId"] = self.make_reference(
                    self._environment.find_by_physical_id(stage_src["apiId"]).logical_id
                )
                found_stage = self._environment.find_by_physical_id(self._parent.logical_id + "Stage" + stage_src["stage"])
                stage["Stage"] = self.make_reference(found_stage.logical_id)
                throttle = {}
                if self.copy_throttle(stage_src, throttle):
                    stage["Throttle"] = throttle
                api_stages.append(stage)
            self._element["ApiStages"] = api_stages

        if "quota" in source_data:
            quota = {}
            self.copy_if_exists("Limit", source_data["quota"], destination_data=quota)
            self.copy_if_exists("Offset", source_data["quota"], destination_data=quota)
            self.copy_if_exists("Period", source_data["quota"], destination_data=quota)
            self._element["Quota"] = quota

        throttle = {}
        if self.copy_throttle(source_data, throttle):
            self._element["Throttle"] = throttle

        self.is_valid = True

        # Get the API Keys
        api_gateway = boto3.client("apigateway")
        keys = api_gateway.get_usage_plan_keys(
            usagePlanId=self.physical_id
        )["items"]
        for key in keys:
            self._environment.add_to_todo(AwsUsagePlanKey(self._environment,key["id"], source_data=key, parent=self))

        return source_data

    def copy_throttle(self, source_data, dest_data) -> bool:
        if "throttle" in source_data:
            throttle = {}
            self.copy_if_exists("BurstLimit", source_data["throttle"], destination_data=dest_data)
            self.copy_if_exists("RateLimit", source_data["throttle"], destination_data=dest_data)
            return True
        return False
