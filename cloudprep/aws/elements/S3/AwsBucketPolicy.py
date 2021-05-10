from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet


class AwsBucketPolicy(AwsElement):
    def __init__(self, environment, **kwargs):
        super().__init__(environment, "AWS::S3::BucketPolicy", kwargs["bucket_name"]+"Policy", **kwargs)
        self._bucket = kwargs["bucket_name"]
        self._policy_doc = kwargs["policy_data"]


    @AwsElement.capture_method
    def capture(self):
        self._element["Bucket"] = self._bucket
        # TODO: Handle any external Resources
        self._element["PolicyDocument"] = self._policy_doc
        self.is_valid = True
