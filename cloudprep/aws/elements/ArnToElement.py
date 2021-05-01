from ..AwsEnvironment import AwsEnvironment
from .AwsARN import AwsARN
from .Lambda.AwsLambdaFunction import AwsLambdaFunction

def element_from_arn(environment: AwsEnvironment, arn: AwsARN):
    if arn.service == "lambda":
        if arn.resource_type == "function":
            return AwsLambdaFunction.create_from_arn(environment, arn)
