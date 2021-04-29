import boto3
from .elements.EC2.AwsVpc import AwsVpc
from .elements.Lambda.AwsLambdaFunction import AwsLambdaFunction
from .AwsEnvironment import AwsEnvironment


class AwsInterrogator:
    def __init__(self, environment=AwsEnvironment()):
        self._environment = environment
        pass

    def start_vpc(self):
        # start with some VPCs!
        ec2 = boto3.client("ec2")
        vpcs = ec2.describe_vpcs()
        for VPC in vpcs["Vpcs"]:
            this_vpc = AwsVpc(self._environment, VPC["VpcId"])
            self._environment.add_to_todo(this_vpc)

    def start_lambda(self):
        lmb = boto3.client("lambda")
        functions = lmb.list_functions()
        for funct in functions["Functions"]:
            self._environment.add_to_todo(AwsLambdaFunction(self._environment, funct["FunctionName"], source_data=funct))

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
