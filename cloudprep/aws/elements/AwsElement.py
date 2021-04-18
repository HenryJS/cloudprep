import hashlib


class AwsElement:
    def __init__(self, awsType, environment, physicalId):
        self._environment = environment

        self._awsType = awsType
        self._logical_id = AwsElement.CalculateLogicalId(awsType, physicalId)
        self._defaults = {}
        self._element = {}
        self._tags = None
        self._valid = False
        self._physical_id = physicalId
        self._source_json = None

    def getLogicalId(self):
        return self._logical_id

    def getPhysicalId(self):
        return self._physical_id

    def getType(self):
        return self._awsType

    def getProperties(self):
        return self._element

    def set_source_json(self, json):
        self._source_json = json

    def makeValid(self):
        self._valid = True

    def isValid(self):
        return self._valid

    def get_tags(self):
        if self._tags:
            return self._tags.get_tags()
        else:
            return None

    def setDefaults(self, defaults):
        self._defaults = defaults

    def isDefault(self, key, value=None):
        if key not in self._defaults:
            return False
        if value is None:
            value = self._element[key]
        return value == self._defaults[key]

    def copyIfExists(self, key, sourceJson):
        if key in sourceJson:
            self._element[key] = sourceJson[key]

    def capture(self):
        raise NotImplementedError("capture is not implemented in this class.")

    @staticmethod
    def CalculateLogicalId(awsType, physicalId):
        # newPID = str(abs(hash(physicalId)))
        MD5 = hashlib.md5()
        MD5.update(physicalId.encode("utf-8"))
        newPid = MD5.hexdigest()[0:16].upper()
        return awsType[awsType.rfind(":") + 1:].lower() + str(newPid)
        # ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
