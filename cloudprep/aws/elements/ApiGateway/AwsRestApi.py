import boto3
from ..AwsARN import AwsARN
from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet


class AwsRestApi(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::ApiGateway::RestApi", physical_id, **kwargs)
        self.set_defaults({
        })
        self._tags = TagSet({"CreatedBy": "CloudPrep"})

    @AwsElement.capture_method
    def capture(self):
        s3 = boto3.client("apigatewayv2")



        api_gateway = boto3.client("apigateway")
        if self._source_data is None:
            source_data = api_gateway.get_rest_api(restApiId=self.physical_id)
        else:
            source_date = self._source_data
            self._source_data = None

        # TODO: "ApiKeySourceType" : String,
        # TODO: "BinaryMediaTypes" : [ String, ... ],
        # TODO: "Body" : Json,
        # TODO: "BodyS3Location" : S3Location,
        # TODO: "CloneFrom" : String,
        self.copy_if_exists("Description", source_data, "description")
        # TODO: "DisableExecuteApiEndpoint" : Boolean,
        # TODO: "EndpointConfiguration" : EndpointConfiguration,
        # TODO: "FailOnWarnings" : Boolean,
        # TODO: "MinimumCompressionSize" : Integer,
        # TODO: "Mode" : String,
        # TODO: "Name" : String,
        # TODO: "Parameters" : {Key: Value, ...},
        # TODO: "Policy" : Json,
        self._tags.from_api_result(source_data)

        self.is_valid = True



    def wrap_call(self, call):
        try:
            result = call()
        except Exception:
            return None
        return result
