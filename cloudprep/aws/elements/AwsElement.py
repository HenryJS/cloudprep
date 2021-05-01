import sys
from typing import final

from ..AwsEnvironment import AwsEnvironment
from .AwsARN import AwsARN


class AwsElement:
    def __init__(self, environment: AwsEnvironment, aws_type, physical_id, **kwargs):
        self._environment = environment

        self._dependencies = []

        # Properties
        self._logical_id = self.calculate_logical_id(physical_id)
        self._aws_type = aws_type
        self._element = {}
        self._valid = False
        self._physical_id = physical_id

        self._tags = None
        if "source_data" in kwargs:
            self._source_data = kwargs["source_data"]
        else:
            self._source_data = None

        self._defaults = {}

    @property
    def logical_id(self):
        return self._logical_id

    @property
    def physical_id(self):
        return self._physical_id

    @property
    def type(self):
        return self._aws_type

    @property
    def properties(self):
        return self._element

    @property
    def is_valid(self):
        return self._valid

    @is_valid.setter
    def is_valid(self, validity):
        self._valid = validity

    @property
    def dependencies(self):
        return self._dependencies

    def add_dependency(self, new_dependency):
        if new_dependency not in self._dependencies:
            self._dependencies.append(new_dependency)

    @property
    def tags(self):
        if self._tags:
            return self._tags.tags
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

    def copy_if_exists(self, key, source_data):
        """ If a key exists, copy it directly"""
        if source_data and key in source_data:
            self._element[key] = source_data[key]

    def refer_if_exists(self, key, source_data):
        """" If a key exists, turn it into a reference and copy it here """
        if source_data and key in source_data:
            self._element[key] = self.make_reference(physical_id=source_data[key])

    def array_refer_if_exists(self, key, source_data):
        """ If a key exists, and is an array, iterate through it and make references. """
        if source_data and key in source_data and isinstance(source_data[key], list):
            self._element[key] = []
            for entry in source_data[key]:
                self._element[key].append(self.make_reference(physical_id=entry))

    @property
    def reference(self):
        return self.make_reference()

    def make_reference(self, logical_id=None, physical_id=None):
        """ Construct a reference for either this object or from a logical or physical id."""
        if logical_id is None:
            if physical_id is None:
                logical_id = self.logical_id
            else:
                logical_id = self.calculate_logical_id(physical_id)

        return {"Ref": logical_id}

    def make_getatt(self, attribute):
        return {"Fn::GetAtt": [self.logical_id, attribute]}

    @staticmethod
    def calculate_logical_id(physical_id):
        return physical_id.replace("-", "")

    def capture_method(f):
        def transformed_method(self):
            print("Capturing %s %s" % (self._aws_type, self._physical_id), file=sys.stderr)
            return f(self)
        return transformed_method

    @capture_method
    def capture(self):
        raise NotImplementedError("capture is not implemented in this class.")

    def finalise_method(f):
        def transformed_method(self):
            print("Finalising %s %s" % (self._aws_type, self._physical_id), file=sys.stderr)
            return f(self)
        return transformed_method

    @finalise_method
    def finalise(self):
        """ Perform any steps required in order to finish up the object.  Returns True if this method
        generates more work for the interrogator to perform; False otherwise. """
        return False

    @staticmethod
    def create_from_arn(arn: AwsARN):
        return None