import hashlib

from ..AwsEnvironment import AwsEnvironment


class AwsElement:
    def __init__(self, aws_type, environment: AwsEnvironment, physical_id, source_json=None):
        self._environment = environment

        self._awsType = aws_type
        self._logical_id = self.calculate_logical_id(aws_type, physical_id)
        self._defaults = {}
        self._element = {}
        self._tags = None
        self._valid = False
        self._physical_id = physical_id
        self._source_json = source_json

    def get_logical_id(self):
        return self._logical_id

    def get_physical_id(self):
        return self._physical_id

    def get_type(self):
        return self._awsType

    def get_properties(self):
        return self._element

    def set_source_json(self, json):
        self._source_json = json

    def make_valid(self, validity=True):
        self._valid = validity

    def is_valid(self):
        return self._valid

    def get_tags(self):
        if self._tags:
            return self._tags.get_tags()
        else:
            return None

    def set_defaults(self, defaults):
        self._defaults = defaults

    def is_default(self, key, value=None):
        if key not in self._defaults:
            return False
        if value is None:
            value = self._element[key]
        return value == self._defaults[key]

    def copy_if_exists(self, key, source_json):
        if key in source_json:
            self._element[key] = source_json[key]

    def make_reference(self):
        return {"Ref": self.get_logical_id()}

    def capture(self):
        raise NotImplementedError("capture is not implemented in this class.")

    def finalise(self):
        return False

    @staticmethod
    def calculate_logical_id(aws_type, physical_id):
        # newPID = str(abs(hash(physicalId)))
        md5 = hashlib.md5()
        md5.update(physical_id.encode("utf-8"))
        new_pid = md5.hexdigest()[0:16].upper()
        return aws_type[aws_type.rfind(":") + 1:].lower() + str(new_pid)
        # ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
