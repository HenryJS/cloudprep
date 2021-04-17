import boto3
from .AwsVpc import AwsVpc

class AwsInterrogator:
    def __init__(self):
        pass

    def interrogateVpcs(self, environment):
        results = []

        EC2=boto3.client("ec2")
        VPCs = EC2.describe_vpcs()
        for VPC in VPCs["Vpcs"]:
            thisVpc = AwsVpc(environment)
            thisVpc.capture(VPC)
            environment.resources.append(thisVpc)

        return results
