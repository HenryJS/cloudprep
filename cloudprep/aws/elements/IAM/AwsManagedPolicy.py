from .AwsPolicy import AwsPolicy


class AwsManagedPolicy(AwsPolicy):
    def __init__(self, environment, arn, **kwargs):
        super().__init__(environment, "AWS::IAM::ManagedPolicy", arn, **kwargs)

    @AwsPolicy.policy_capture
    def capture(self, this_policy, this_version):
        self.is_valid = True
        return
