from .AwsPolicy import AwsPolicy
from ..AwsElement import AwsElement


class AwsInlinePolicy(AwsElement):
    def __init__(self, environment, arn, **kwargs):
        super().__init__(environment, "AWS::IAM::Policy", arn, **kwargs)

    @AwsPolicy.policy_capture
    def capture(self, this_policy, this_version):

        # PolicyName is required and it needs to be made unique.  However, the policy we're reading from
        # may introduce clashes.  Hashing it, then appending it, is a way to make it repeatedly different for this
        # script. It'll clash if the script is invoked twice but you can't have everything.
        self._element["PolicyName"] = self.make_unique(self.logical_id)

        self.is_valid = True

