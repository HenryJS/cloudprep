import boto3
import sys
import requests
import os
import hashlib
from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet
from ..IAM.AwsRole import AwsRole
from ..AwsARN import AwsARN
from ....ArtefactRepository import ArtefactRepository
from ....Artefact import Artefact


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
        self.copy_if_exists("Handler", configuration)
        self.copy_if_exists("MemorySize", configuration)
        self.copy_if_exists("Runtime", configuration)
        self.copy_if_exists("Timeout", configuration)

        role = AwsRole(self._environment, AwsARN(configuration["Role"]))
        self._element["Role"] = role.make_getatt("Arn")

        # // TODO: This can be broken
        if "Tags" in source_data:
            self._tags.from_api_result(source_data)

        if "Concurrency" in source_data:
            self.copy_if_exists("ReservedConcurrentExecutions", source_data["Concurrency"])

        # Code. This is complex.
        if source_data["Code"]["RepositoryType"] == "S3":
            self._code_s3(source_data["Code"])

        self.is_valid = True


    def  create_from_arn(environment, arn: AwsARN, **kwargs):
        return AwsLambdaFunction(environment, arn.resource_id, **kwargs)


    def _code_s3(self, code_data):
        code_request = requests.get(code_data["Location"])
        if code_request.status_code != 200:
            raise Exception("Couldn't download code bundle from " + code_data["Location"])

        afr = ArtefactRepository.get_repository()
        code_artefact = Artefact("lambda-" + self.logical_id + "-code.zip", code_request.content)
        afr.store_artefact(code_artefact)

        self._environment.add_parameter(
            Name="ArtefactBucket",
            Description="The bucket in which our artefacts are stored."
        )
        self._environment.add_parameter(
            Name=self.logical_id + "CodeKey",
            Description="The key for the " + self.logical_id + " lambda code package.",
            Default=code_artefact.name
        )
        self._element["Code"] = {
            "S3Bucket": {"Ref": "ArtefactBucket"},
            "S3Key": {"Ref": self.logical_id + "CodeKey"}
        }