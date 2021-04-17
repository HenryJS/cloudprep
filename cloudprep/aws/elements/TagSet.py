class TagSet:
    def __init__(self, tagDict = None):
        if tagDict:
            self.__tags = tagDict
        else:
            self.__tags = {}

    def addTag(self, key, value):
        if not key.startswith("aws:"):
            self.__tags[key] = value

    def toCfn(self):
        cfn = []
        for (key,value) in self.__tags.items():
            cfn.append({ "Key": key, "Value": value})
        return cfn

    def fromCfn(self, cfn):
        for tag in cfn:
            self.addTag(tag["Key"], tag["Value"])