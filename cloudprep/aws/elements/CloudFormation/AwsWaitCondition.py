from cloudprep.aws.elements.AwsElement import AwsElement
from .AwsWaitConditionHandle import AwsWaitConditionHandle


class AwsWaitCondition(AwsElement):
    def __init__(self, environment, physical_id, timeout):
        super().__init__(environment, "AWS::EC2::WaitCondition", physical_id, None)
        self._timeout = timeout
        self.set_defaults({})

    @AwsElement.capture_method
    def capture(self):
        wait_handle = AwsWaitConditionHandle(self._environment, self.physical_id + "-handle")
        self._environment.add_to_todo(wait_handle)

        self._element["Handle"] = wait_handle.make_reference()
        self._element["Timeout"] = self._timeout

        self.make_valid()
