import boto3
import sys
from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet
from ..IAM.AwsRole import AwsRole
from ..AwsARN import AwsARN


class AwsLambdaFunction(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::Lambda::Function", physical_id, **kwargs)
        self.set_defaults({
            "Description": "",
            "MemorySize": 128,
            "ReservedConcurrentExecutions": 1000,
            "Timeout": 3
        })
        self._tags = TagSet({"CreatedBy": "CloudPrep"})

    @AwsElement.capture_method
    def capture(self):
        # {
        #   "Type" : "AWS::Lambda::Function",
        #   "Properties" : {
        #       *"Code" : Code,
        #       "CodeSigningConfigArn" : String,
        #       "DeadLetterConfig" : DeadLetterConfig,
        #       "FileSystemConfigs" : [ FileSystemConfig, ... ],
        #       "ImageConfig" : ImageConfig,
        #       "KmsKeyArn" : String,
        #       "Layers" : [ String, ... ],
        #       "PackageType" : String,
        #       "TracingConfig" : TracingConfig,
        #       "VpcConfig" : VpcConfig
        #     }
        # }
        lmb = boto3.client("lambda")
        source_data = lmb.get_function(FunctionName=self.physical_id)
        configuration = source_data["Configuration"]
        self._source_data = None

        self.copy_if_exists("Description", configuration)
        self.copy_if_exists("Environment", configuration)
        self.copy_if_exists("FunctionName", configuration)
        self.copy_if_exists("Handler", configuration)
        self.copy_if_exists("MemorySize", configuration)
        self.copy_if_exists("Runtime", configuration)  # TODO: what is the default?
        self.copy_if_exists("Timeout", configuration)
        role = AwsRole(self._environment, AwsARN(configuration["Role"]))
        self._element["role"] = role.arn_reference
        self._environment.add_to_todo(role)

        #TODO: Sort tags
        # self._tags.from_api_result(configuration)

        self._environment.add_parameter(**{ "Name": "Code URI" })
        self.is_valid = True

    # @staticmethod
    # def calculate_logical_id(physical_id):
    #     return "Lambda" + physical_id.replace("-", "")

    def  create_from_arn(environment, arn: AwsARN, **kwargs):
        return AwsLambdaFunction(environment, arn.resource_id, **kwargs)