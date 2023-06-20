import json

import boto3
from .elements.EC2.AwsVpc import AwsVpc
from .elements.Lambda.AwsLambdaFunction import AwsLambdaFunction
from .elements.IAM.AwsRole import AwsRole
from .elements.S3.AwsBucket import AwsBucket
from .elements.KMS.AwsKmsKey import AwsKmsKey
from .elements.KMS.AwsKmsAlias import AwsKmsAlias
from .elements.AwsARN import AwsARN
from .elements.ArnToElement import element_from_arn
from .elements.StepFunctions.AwsStateMachine import AwsStateMachine
from .elements.ApiGateway.AwsRestApi import AwsRestApi
from .AwsEnvironment import AwsEnvironment


class AwsInterrogator:
    def __init__(self, environment=AwsEnvironment()):
        self._environment = environment
        pass

    def start_vpc(self, vpc_id):
        if vpc_id is True:
            # start with some VPCs!
            ec2 = boto3.client("ec2")
            vpcs = ec2.describe_vpcs()
            for VPC in vpcs["Vpcs"]:
                this_vpc = AwsVpc(self._environment, VPC["VpcId"])
                self._environment.add_to_todo(this_vpc)
        else:
            self._environment.add_to_todo(AwsVpc(self._environment, vpc_id))

    def start_lambda(self, id):
        if id is True:
            lmb = boto3.client("lambda")
            functions = lmb.list_functions()
            for funct in functions["Functions"]:
                self._environment.add_to_todo(AwsLambdaFunction(self._environment, funct["FunctionName"], source_data=funct))
        else:
            self._environment.add_to_todo(element_from_arn(self._environment, AwsARN(id)))

    def start_role(self, text_arn):
        arn = AwsARN(text_arn)
        self._environment.add_to_todo(AwsRole(self._environment, arn))

    def start_stepfn(self, stepfn):
        if stepfn is True:
            # start with some VPCs!
            sfn = boto3.client("stepfunctions")
            fns = sfn.list_state_machines()
            for FN in fns["stateMachines"]:
                self._environment.add_to_todo(AwsStateMachine(self._environment, AwsARN(FN["stateMachineArn"])))
        else:
            self._environment.add_to_todo(AwsStateMachine(self._environment, AwsARN(stepfn)))

    def start_bucket(self, bucket_name):
        s3 = boto3.client("s3")
        if bucket_name is True:
            bucket_response = s3.list_buckets()
            for bucket in bucket_response["Buckets"]:
                self._environment.add_to_todo(AwsBucket(self._environment, bucket["Name"]))
        else:
            self._environment.add_to_todo(AwsBucket(self._environment, bucket_name))

    def start_kms_key(self, kms_key):
        kms = boto3.client("kms")
        if kms_key is True:
            response = kms.list_keys()
            for key in response["Keys"]:
                self._environment.add_to_todo(AwsKmsKey(self._environment, key["KeyId"], KmsAliasCreator=AwsKmsAlias))
        else:
            arn = AwsARN(kms_key)
            self._environment.add_to_todo(AwsKmsKey(self._environment, arn.resource_id, KmsAliasCreator=AwsKmsAlias))

    def start_kms_alias(self, kms_alias):
        self._environment.add_to_todo(AwsKmsAlias(self._environment, kms_alias))

    def start_rest_api(self, rest_api_id):
        self._environment.add_to_todo(AwsRestApi(self._environment, rest_api_id))

    def interrogate(self):
        more_work = True
        while more_work:
            self.capture_elements()
            more_work = self.finalise_elements()

        return self._environment

    def capture_elements(self):
        element = self._environment.get_next_todo()
        while element is not None:
            element.capture()
            self._environment.add_resource(element)
            self._environment.remove_from_todo(element)
            element = self._environment.get_next_todo()

    def finalise_elements(self):
        more_work_to_do = False
        for key, element in self._environment.resources.items():
            more_work_to_do = more_work_to_do or element.finalise()

        return more_work_to_do
