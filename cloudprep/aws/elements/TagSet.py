class TagSet:
    def __init__(self, tagDict = None):
        if tagDict:
            self._tags = tagDict
        else:
            self._tags = {}

    def addTag(self, key, value):
        if not key.startswith("aws:"):
            self._tags[key] = value

    def getTags(self):
        return self._tags

    def fromApiResult(self, cfn):
        if "Tags" in cfn:
            cfn = cfn["Tags"]
        for tag in cfn:
            self.addTag(tag["Key"], tag["Value"])