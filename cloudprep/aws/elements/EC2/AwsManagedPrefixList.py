import boto3

from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet


class AwsManagedPrefixList(AwsElement):
    def __init__(self, environment, physical_id, **kwargs):
        super().__init__(environment, "AWS::EC2::PrefixList", physical_id, **kwargs)
        self._physical_id = physical_id
        self._tags = TagSet()

    @AwsElement.capture_method
    def capture(self):
        ec2 = boto3.client("ec2")
        source_data = ec2.describe_managed_prefix_lists(PrefixListIds=[self._physical_id])["PrefixLists"][0]
        if source_data["OwnerId"] == "AWS":
            raise Exception("Prefix list " + self._physical_id + " appears to be AWS-managed.")

        self.copy_if_exists("AddressFamily", source_data)
        self.copy_if_exists("MaxEntries", source_data)
        self.copy_if_exists("PrefixListName", source_data)
        self.copy_if_exists("Entries", ec2.get_managed_prefix_list_entries(PrefixListId=self._physical_id))
        self._tags.from_api_result(source_data)

        self.is_valid = True
