import boto3
from .AwsVpc import AwsVpc

class AwsInterrogator:
    def __init__(self):
        pass

    def interrogate(self, environment):
        # start with some VPCs!
        EC2 = boto3.client("ec2")
        VPCs = EC2.describe_vpcs()
        for VPC in VPCs["Vpcs"]:
            thisVpc = AwsVpc(environment, VPC["VpcId"])
            environment.addToTodo(thisVpc)

        element = environment.getNextTodo()
        while element is not None:
            element.capture()
            environment.resources.append(element)
            environment.removeFromTodo(element)
            element = environment.getNextTodo()

    # def interrogateVpcs(self, environment):
    #     results = []
    #
    #     EC2=boto3.client("ec2")
    #     VPCs = EC2.describe_vpcs()
    #     for VPC in VPCs["Vpcs"]:
    #         thisVpc = AwsVpc(environment)
    #         thisVpc.capture(VPC)
    #         environment.resources.append(thisVpc)
    #
    #     return results
