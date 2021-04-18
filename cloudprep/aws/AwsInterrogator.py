import boto3
from cloudprep.aws.elements.EC2.AwsVpc import AwsVpc
from .AwsEnvironment import AwsEnvironment


class AwsInterrogator:
    def __init__(self):
        pass

    def interrogate(self, environment=AwsEnvironment()):
        # start with some VPCs!
        EC2 = boto3.client("ec2")
        VPCs = EC2.describe_vpcs()
        for VPC in VPCs["Vpcs"]:
            thisVpc = AwsVpc(environment, VPC["VpcId"])
            environment.addToTodo(thisVpc)

        element = environment.get_next_todo()
        while element is not None:
            element.capture()
            environment.add_resource(element)
            environment.remove_from_todo(element)
            element = environment.get_next_todo()

        return environment
