import boto3, sys
from cloudprep.aws.elements.AwsElement import AwsElement
from ..IAM.AwsRole import AwsRole
from ..AwsARN import AwsARN
from ..Lambda.AwsLambdaFunction import AwsLambdaFunction


class AwsMethod(AwsElement):
    def __init__(self, environment, **kwargs):
        self._http_method = kwargs["http_method"]
        self._resource_id = kwargs["resource_id"]
        physical_id = kwargs["parent"].logical_id + self._resource_id + self._http_method

        super().__init__(environment, "AWS::ApiGateway::Method", physical_id, **kwargs)

        self.set_defaults({})

    @AwsElement.capture_method
    def capture(self):
        api_gateway = boto3.client("apigateway")
        if self._source_data is None:
            source_data = api_gateway.get_method(
                restApiId=self._parent.logical_id,
                resourceId=self._resource_id,
                httpMethod=self._http_method
            )
        else:
            source_data = self._source_data
            self._source_data = None

        self.copy_if_exists("ApiKeyRequired", source_data, "apiKeyRequired")
        # TODO: "AuthorizationScopes": [String, ...], - COGNITO

        # TODO: CUSTOM and COGNITO_USER_POOLS authorization types
        self.copy_if_exists("AuthorizationType", source_data, "authorizationType")
        if self._element["AuthorizationType"] not in ["NONE", "IAM"]:
            raise NotImplementedError("Api Gateway capture only supports NONE and IAM authorization types.")

        # TODO: "AuthorizerId": String, = CISTP< pr C+I+{
        self._element["HttpMethod"] = self._http_method
        # TODO: "ConnectionId": String,

        if "methodIntegration" in source_data:
            i = source_data["methodIntegration"]
            # All elements are optional
            integration = {}

            # To be valid CFN, these must also be present in RequestParameters.  As we are reading this from
            # a life environment, assume that this constraint holds true.
            self.copy_if_exists("CacheKeyParameters", i, destination_data=integration)
            if "cacheNamespace" in i:
                if i["cacheNamespace"] != self._resource_id:
                    integration["CacheNamespace"] = i["cacheNamespace"]

            self.copy_if_exists("ContentHandling", i, destination_data=integration)
            self.copy_if_exists("ConnectionType", i, destination_data=integration)

            if "credentials" in i:
                if i["credentials"].startswith("arn:aws:iam"):
                    if "*:user/*" in i["credentials"]:
                        integration["Credentials"] = i["credentials"]
                    else:
                        role = AwsRole(
                            self._environment,
                            AwsARN(i["credentials"])
                        )
                        self._environment.add_to_todo(role)
                        integration["Credentials"] = self.make_reference(role.logical_id)

            self.copy_if_exists("IntegrationHttpMethod", i, "httpMethod", destination_data=integration)

            if "integrationResponses" in i:
                ir = []
                for key, response in i["integrationResponses"].items():
                    resp = {
                        "StatusCode": response["statusCode"]
                    }
                    self.copy_if_exists("ContentHandling", response, destination_data=resp)
                    self.copy_if_exists("SelectionPattern", response, destination_data=resp)
                    if "responseModels" in response:
                        resp["ResponseModels"] = response["responseModels"].copy()
                    if "responseParameters" in response:
                        resp["ResponseParameters"] = response["responseParameters"].copy()
                    ir.append(resp)
                integration["IntegrationResponses"] = ir
            # End Integration->IntegrationResponses

            self.copy_if_exists("PassThroughBehaviour", i, destination_data=integration)
            self.copy_if_exists("RequestParameters", i, destination_data=integration)
            self.copy_if_exists("RequestTemplates", i, destination_data=integration)
            self.copy_if_exists("TimeoutInMillis", i, destination_data=integration)
            self.copy_if_exists("Type", i, destination_data=integration)
            # TODO: Deal with this properly!
            # TODO: S3 Integration
            # TODO: API Gateway Integration
            # TODO: Lambda Integration
            # TODO: VPC_LINK NLB DNS names

            if "uri" in i:
                uri = i["uri"]
                uri_arn = AwsARN(uri)
                print(uri, file=sys.stderr)
                if uri_arn.account == "lambda":
                    lambda_arn = AwsARN(uri_arn.resource_path.split("/")[3])
                    llambda = AwsLambdaFunction(self._environment, lambda_arn.resource_id)
                    new_uri = {
                        "Fn::Sub": 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/' + \
                            '${' + llambda.logical_id + '.Arn}/invocations'
                    }
                    integration["Uri"] = new_uri
                    self._environment.add_to_todo(llambda)

                else:
                    self.copy_if_exists("Uri", i, destination_data=integration)
            self._element["Integration"] = integration
        # END MethodIntegration

        if "methodResponses" in source_data:
            mr = []
            for key,response in source_data["methodResponses"].items():
                resp = {
                    "StatusCode": response["statusCode"]
                }
                if "responseModels" in response:
                    resp["ResponseModels"] = response["responseModels"].copy()
                if "responseParameters" in response:
                    resp["ResponseParameters"] = response["responseParameters"].copy()
                mr.append(resp)
            self._element["MethodResponses"] = mr

        self.copy_if_exists("OperationName", source_data, "operationName")
        # TODO: "RequestModels": {Key: Value, ...},
        # TODO: "RequestParameters": {Key: Value, ...},
        # TODO: "RequestValidatorId": String,

        self._element["ResourceId"] = self.make_reference(self._resource_id)
        self._element["RestApiId"] = self.make_reference(self._parent.logical_id)

        self.is_valid = True
