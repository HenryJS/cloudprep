class TagSet:
    def __init__(self, tag_dictionary=None):
        if tag_dictionary:
            self._tags = tag_dictionary
        else:
            self._tags = {}

    def add_tag(self, key, value):
        if not key.startswith("aws:"):
            self._tags[key] = value

    def get_tags(self):
        return self._tags

    def from_api_result(self, cfn):
        if "Tags" in cfn:
            cfn = cfn["Tags"]
        for tag in cfn:
            self.add_tag(tag["Key"], tag["Value"])
