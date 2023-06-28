from ..AwsElement import AwsElement
from ..TagSet import TagSet


class AwsEIP(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::EC2::EIP", physical_id, **kwargs)
        self._tags = TagSet()
        self.set_defaults({
            "Domain": "vpc"
        })

    @AwsElement.capture_method
    def capture(self):
        # if self._source_data is None:
        #     source_data = None
        #     pass
        # else:
        # {
        #   "Type" : "AWS::EC2::EIP",
        #   "Properties" : {
        #       "Domain" : String,
        #       "InstanceId" : String,
        #       "PublicIpv4Pool" : String,
        #     }
        # }
        source_data = self._source_data
        self._source_data = None

        if "Tags" in source_data:
            self._tags.from_api_result(source_data["Tags"])

        self.is_valid = True
