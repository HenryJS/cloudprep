import boto3

from cloudprep.aws.elements.AwsElement import AwsElement
from .AwsApiKey import AwsApiKey


class AwsUsagePlanKey(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::ApiGateway::UsagePlanKey", physical_id, **kwargs)
        self._logical_id_prefix = "usageplankey"
        self.set_defaults({})

    @AwsElement.capture_method
    def capture(self):
        api_gateway = boto3.client("apigateway")

        if self._source_data is None:
            source_data = None
            pass
        else:
            source_data = self._source_data
            self._source_data = None

        api_key = AwsApiKey(self._environment, "apikey" + source_data["id"], id=source_data["id"])
        self._environment.add_to_todo(api_key)

        self._element["KeyType"] = "API_KEY"
        self._element["KeyId"] = self.make_reference(api_key.logical_id)
        self._element["UsagePlanId"] = self.make_reference(self._parent.logical_id)

        self.is_valid = True

