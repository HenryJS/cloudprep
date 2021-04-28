from ..AwsElement import AwsElement
from ..TagSet import TagSet


class AwsEIP(AwsElement):
    def __init__(self, environment, physical_id, source_json=None):
        super().__init__("AWS::EC2::EIP", environment, physical_id, source_json)
        self._tags = TagSet({"CreatedBy": "CloudPrep"})
        self.set_defaults({
            "Domain": "vpc"
        })

    @AwsElement.capture_method
    def capture(self):
        # if self._source_json is None:
        #     source_json = None
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
        source_json = self._source_json
        self._source_json = None

        if "Tags" in source_json:
            self._tags.from_api_result(source_json["Tags"])

        self.make_valid()
