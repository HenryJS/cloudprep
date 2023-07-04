import boto3, sys

from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet


class AwsApiKey(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::ApiGateway::ApiKey", physical_id, **kwargs)
        # self._logical_id = "apikey" + self._logical_id
        self.set_defaults({})
        self._tags = TagSet()
        self._id = kwargs["id"]

    @AwsElement.capture_method
    def capture(self):
        api_gateway = boto3.client("apigateway")
        source_data = api_gateway.get_api_key(apiKey=self._id, includeValue=True)
        self._environment.add_warning("API Key to be re-generated.  Please inform your users.", self.physical_id)

        self.copy_if_exists("CustomerId", source_data)
        self.copy_if_exists("Description", source_data)
        self.copy_if_exists("Enabled", source_data)
        #         "Name": String, // ignored - aws can generate it
        self._tags.from_api_result(source_data)

        self.is_valid = True
