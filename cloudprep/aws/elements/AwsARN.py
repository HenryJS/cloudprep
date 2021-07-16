class AwsARN:
    def __init__(self, arn):
        self._text = arn
        components = arn.split(":")
        if len(components) == 7:
            _type, self._partition, self._service, self._region, \
                self._account, self._resource_type, self._resource_id = components
            self._format = 1
        elif len(components) == 6:
            _type, self._partition, self._service, self._region, \
                self._account, resource = components

            resource = resource.split("/")
            if len(resource) == 1:
                self._resource_type = None
                self._resource_path = None
                self._resource_id = resource[0]
                self._format = 2

            elif len(resource) == 2:
                self._resource_type = resource[0]
                self._resource_path = None
                self._resource_id = resource[1]
                self._format = 3

            else:
                self._resource_type = resource[0]
                self._resource_path = "/" + "/".join(resource[1:-1]) + "/"
                self._resource_id = resource[-1]
                self._format = 4

        elif len(components) == 8:
            # This probably only applies to LowGroup ARNs?
            # arn:aws:logs:eu-west-2:368255555983:log-group:/aws/vendedlogs/states/HelloWorld-Logs:*
            _type, self._partition, self._service, self._region, \
                self._account, self._resource_type, self._resource_id, self._inner_resource = components

        else:
            raise Exception("Unfamiliar format: {} has {} groups.".format(arn, len(components)))

    @property
    def text(self):
        if self._format == 1:
            return ":".join([
                "arn", self._partition, self._service, self._region, self._account,
                self._resource_type, self._resource_id
            ])
        elif self._format == 2:
            return ":".join([
                "arn", self._partition, self._service, self._region, self._account,
                self._resource_id
            ])
        elif self._format == 3:
            return ":".join([
                "arn", self._partition, self._service, self._region, self._account,
                "/".join([self._resource_type, self._resource_id])
            ])
        elif self._format == 4:
            return ":".join([
                "arn", self._partition, self._service, self._region, self._account,
                "/".join([self._resource_type, self._resource_path, self._resource_id])
            ])


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

    @resource_type.setter
    def resource_type(self, new_type):
        self._resource_type = new_type

    @property
    def resource_id(self):
        return self._resource_id

    @resource_id.setter
    def resource_id(self, new_id):
        self._resource_id = new_id

    @property
    def resource_path(self):
        return self._resource_path

    @property
    def inner_resource(self):
        return self._inner_resource
