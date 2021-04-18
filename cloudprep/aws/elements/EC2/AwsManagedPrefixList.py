import boto3

from cloudprep.aws.elements.AwsElement import AwsElement
from cloudprep.aws.elements.TagSet import TagSet


class AwsManagedPrefixList(AwsElement):
    def __init__(self, environment, phyiscalId):
        super().__init__("AWS::EC2::PrefixList", environment, phyiscalId)
        self._physical_id = phyiscalId
        self._tags = TagSet({"CreatedBy": "CloudPrep"})

    def capture(self):
        EC2 = boto3.client("ec2")
        sourceJson = EC2.describe_managed_prefix_lists(PrefixListIds=[self._physical_id])["PrefixLists"][0]
        if sourceJson["OwnerId"] == "AWS":
            raise Exception("Prefix list " + self._physical_id + " appears to be AWS-managed.")

        self.copyIfExists("AddressFamily", sourceJson)
        self.copyIfExists("MaxEntries", sourceJson)
        self.copyIfExists("PrefixListName", sourceJson)
        self.copyIfExists("Entries", EC2.get_managed_prefix_list_entries(PrefixListId=self._physical_id))
        self._tags.from_api_result(sourceJson)

        self.makeValid()
