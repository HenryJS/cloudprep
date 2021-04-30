class AwsARN:
    def __init__(self, arn):
        self._text = arn
        components = arn.split(":")
        if len(components) == 7:
            _type, self._partition, self._service, self._region, \
                self._account, self._resource_type, self._resource_id = components
        elif len(components) == 6:
            _type, self._partition, self._service, self._region, \
                self._account, resource = components

            resource = resource.split("/")
            if len(resource) == 1:
                self._resource_type = None
                self._resource_path = None
                self._resource_id = resource[0]

            elif len(resource) == 2:
                self._resource_type = resource[0]
                self._resource_path = None
                self._resource_id = resource[1]

            else:
                self._resource_type = resource[0]
                self._resource_path = "/" + "/".join(resource[1:-1]) + "/"
                self._resource_id = resource[-1]

    @property
    def text(self):
        return self._text

    @property
    def partition(self):
        return self._partition

    @property
    def service(self):
        return self._service

    @property
    def region(self):
        return self._region

    @property
    def account(self):
        return self._account

    @property
    def resource_type(self):
        return self._resource_type

    @property
    def resource_id(self):
        return self._resource_id

    @property
    def resource_path(self):
        return self._resource_path
