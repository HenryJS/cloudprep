import random, string

class AwsElement:
    def __init__(self, type, environment):
        self._environment = environment

        self._type = type
        self._logical_prefix = type[type.rfind(":")+1:].lower()
        self._logical_id = self._logical_prefix + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        self._defaults = {}
        self._element = {}

        self._phsysical_id = "NotSet"

    def getLogicalId(self):
        return self._logical_id

    def getPhysicalId(self):
        return self._physical_id

    def getType(self):
        return self._type

    def setDefaults(self, defaults):
        self._defaults = defaults


    def isDefault(self, key, value):
        if key not in self._defaults:
            return False
        return value == self._defaults[key]


    def capture(self):
        raise NotImplementedError("capture is not implemeneted in this class.")


    def _sanitiseTags(self, jsonTags):
        goodTags=[]
        for tag in jsonTags:
            if not tag["Key"].startswith("aws:"):
                goodTags.append(tag)

        return goodTags