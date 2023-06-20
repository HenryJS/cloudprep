import boto3
from cloudprep.aws.elements.AwsElement import AwsElement
from ..IAM.AwsRole import AwsRole
from ..AwsARN import AwsARN


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
        # {
        #     TODO: "ConnectionId": String,
        #     "IntegrationResponses": [IntegrationResponse, ...],
        # }

        if "methodIntegration" in source_data:
            i = source_data["methodIntegration"]
            # All elements are optional
            integration = {}

            # To be valid CFN, these must also be present in RequestParameters.  As we are reading this from
            # a life environment, assume that this constraint holds true.
            self.copy_if_exists_ex(integration, "CacheKeyParameters", i)
            if "cacheNamespace" in i:
                if i["cacheNamespace"] != self._resource_id:
                    integration["CacheNamespace"] = i["cacheNamespace"]

            self.copy_if_exists_ex(integration, "ContentHandling", i)
            self.copy_if_exists_ex(integration, "ConnectionType", i)

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

            self.copy_if_exists_ex(integration, "IntegrationHttpMethod", i, "httpMethod")

            if "integrationResponses" in i:
                ir = []
                for key, response in i["integrationResponses"].items():
                    resp = {
                        "StatusCode": response["statusCode"]
                    }
                    self.copy_if_exists_ex(resp, "ContentHandling", response)
                    self.copy_if_exists_ex(resp, "SelectionPattern", response)
                    if "responseModels" in response:
                        resp["ResponseModels"] = response["responseModels"].copy()
                    if "responseParameters" in response:
                        resp["ResponseParameters"] = response["responseParameters"].copy()
                    ir.append(resp)
                integration["IntegrationResponses"] = ir
            # End Integration->IntegrationResponses

            self.copy_if_exists_ex(integration, "PassThroughBehaviour", i)
            self.copy_if_exists_ex(integration, "RequestParameters", i)
            self.copy_if_exists_ex(integration, "RequestTemplates", i)
            self.copy_if_exists_ex(integration, "TimeoutInMillis", i)
            self.copy_if_exists_ex(integration, "Type", i)
            # TODO: Deal with this properly!
            # TODO: S3 Integration
            # TODO: API Gateway Integration
            # TODO: Lambda Integration
            # TODO: VPC_LINK NLB DNS names
            self.copy_if_exists_ex(integration, "Uri", i)
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
