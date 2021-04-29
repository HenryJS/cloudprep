import boto3
from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet
from ..IAM.AwsRole import AwsRole
from ..AwsARN import AwsARN


class AwsLambdaFunction(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::Lambda::Function", physical_id, **kwargs)
        self.set_defaults({})
        self._tags = TagSet({"CreatedBy": "CloudPrep"})

    @AwsElement.capture_method
    def capture(self):
        self._element["PhysicalId"] = self._physical_id
        # {
        #   "Type" : "AWS::Lambda::Function",
        #   "Properties" : {
        #       *"Code" : Code,
        #       "CodeSigningConfigArn" : String,
        #       "DeadLetterConfig" : DeadLetterConfig,
        #       "Description" : String,
        #       "Environment" : Environment,
        #       "FileSystemConfigs" : [ FileSystemConfig, ... ],
        #       "Handler" : String,
        #       "ImageConfig" : ImageConfig,
        #       "KmsKeyArn" : String,
        #       "Layers" : [ String, ... ],
        #       "MemorySize" : Integer,
        #       "PackageType" : String,
        #       "ReservedConcurrentExecutions" : Integer,
        #       * "Role" : String,
        #       "Runtime" : String,
        #       "Tags" : [ Tag, ... ],
        #       "Timeout" : Integer,
        #       "TracingConfig" : TracingConfig,
        #       "VpcConfig" : VpcConfig
        #     }
        # }
        if self._source_data is None:
            lmb = boto3.client("lambda")
            source_data = lmb.get_function(FunctionName=self.physical_id)
            pass
        else:
            source_data = self._source_data
            self._source_data = None

        self.copy_if_exists("FunctionName", source_data)

        role = AwsRole(self._environment, AwsARN(source_data["Role"]))
        self._element["role"] = role.reference
        self._environment.add_to_todo(role)

        self.is_valid = True

    # @staticmethod
    # def calculate_logical_id(physical_id):
    #     return "Lambda" + physical_id.replace("-", "")

