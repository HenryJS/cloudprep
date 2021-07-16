class AwsARN:
    def __init__(self, arn):
        self._text = arn
        components = arn.split(":")
        if len(components) == 7:
            _type, self._partition, self._service, self._region, \
                self._account, self._resource_type, self._resource_id = components
            self._resource_path = None
            self._inner_resource = None
            self._format = 1

        elif len(components) == 6:
            _type, self._partition, self._service, self._region, \
                self._account, resource = components
            self._resource_path = None
            self._resource_type = None
            self._inner_resource = None

            resource = resource.split("/")
            if len(resource) == 1:
                self._resource_id = resource[0]
                self._format = 2

            elif len(resource) == 2:
                self._resource_type = resource[0]
                self._resource_id = resource[1]
                self._format = 3

            else:
                self._resource_type = resource[0]
                self._resource_path = "/" + "/".join(resource[1:-1]) + "/"
                self._resource_id = resource[-1]
                self._format = 4

        elif len(components) == 8:
            _type, self._partition, self._service, self._region, \
            self._account, self._resource_type, self._resource_id , self._inner_resource = components
            slash_location = self._resource_id.rfind("/")

            if slash_location > 0:
                self._resource_path = self._resource_id[:slash_location]
                self._resource_id = self._resource_id[slash_location+1:]

            self._format = 5

        else:
            raise Exception("Unfamiliar format: {} has {} groups.".format(arn, len(components)))

    @property
    def text(self):
        response = None

        if self._format == 1:
            response = ":".join([
                "arn", self._partition, self._service, self._region, self._account,
                self._resource_type, self._resource_id
            ])
        elif self._format == 2:
            response = ":".join([
                "arn", self._partition, self._service, self._region, self._account,
                self._resource_id
            ])
        elif self._format == 3:
            response = ":".join([
                "arn", self._partition, self._service, self._region, self._account,
                "/".join([self._resource_type, self._resource_id])
            ])
        elif self._format == 4:
            response = ":".join([
                "arn", self._partition, self._service, self._region, self._account,
                "/".join([self._resource_type, self._resource_path, self._resource_id])
            ])
        else:
            raise Exception("Format {} not renderable".format(self._format))

        return response.replace("//","/")

    def prettify(self):
        response = "\n".join([
            "Partition:      {}".format(self.partition),
            "Service:        {}".format(self.service),
            "Region:         {}".format(self.region),
            "Account:        {}".format(self.account),
            "Resource Type:  {}".format(self.resource_type),
            "Resource Path:  {}".format(self.resource_path),
            "Resource ID:    {}".format(self.resource_id),
            "Inner Resource: {}".format(self.inner_resource)
        ])
        return response

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
