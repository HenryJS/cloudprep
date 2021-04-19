import boto3
from cloudprep.aws.elements.EC2.AwsVpc import AwsVpc
from .AwsEnvironment import AwsEnvironment


class AwsInterrogator:
    def __init__(self):
        pass

    @staticmethod
    def interrogate(environment=AwsEnvironment()):
        # start with some VPCs!
        ec2 = boto3.client("ec2")
        vpcs = ec2.describe_vpcs()
        for VPC in vpcs["Vpcs"]:
            this_vpc = AwsVpc(environment, VPC["VpcId"])
            environment.add_to_todo(this_vpc)

        element = environment.get_next_todo()
        while element is not None:
            element.capture()
            environment.add_resource(element)
            environment.remove_from_todo(element)
            element = environment.get_next_todo()

        return environment
