import random, string, hashlib

class AwsElement:
    def __init__(self, type, environment, physicalId):
        self._environment = environment

        self._type = type
        self._logical_id = AwsElement.CalculateLogicalId(type, physicalId)
        self._defaults = {}
        self._element = {}
        self._tags = None

        self._physical_id = physicalId

    def getLogicalId(self):
        return self._logical_id

    def getPhysicalId(self):
        return self._physical_id

    def getType(self):
        return self._type

    def setDefaults(self, defaults):
        self._defaults = defaults

    def isDefault(self, key, value=None):
        if key not in self._defaults:
            return False
        if value is None:
            value = self._element[key]
        return value == self._defaults[key]

    def copyIfExists(self,key,sourceJson):
        if key in sourceJson:
            self._element[key] = sourceJson[key]

    def capture(self):
        raise NotImplementedError("capture is not implemeneted in this class.")


    def CalculateLogicalId(type, physicalId):
        # newPID = str(abs(hash(physicalId)))
        MD5 = hashlib.md5()
        MD5.update(physicalId.encode("utf-8"))
        newPid = MD5.hexdigest()[0:16].upper()
        return type[type.rfind(":") + 1:].lower() + str(newPid)
        # ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
