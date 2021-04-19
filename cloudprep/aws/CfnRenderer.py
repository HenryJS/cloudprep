import json


class CfnRenderer:
    def __init__(self, environment):
        self._environment = environment

    def render(self):
        print(json.dumps(
            {
                "Description": self._environment.description,
                "Mappings": self._environment.mappings,
                "Resources": self.render_resources(self._environment.resources),
                "Outputs": self._environment.outputs
            }, indent=4
        ))

    @staticmethod
    def render_resources(resource_set):
        response = {}
        for physical_id, resource in resource_set.items():
            if not resource.is_valid():
                continue

            r = {
                "Type": resource.get_type(),
                "Properties": {}
            }

            for (prop, value) in resource.get_properties().items():
                if not resource.is_default(prop):
                    r["Properties"][prop] = value

            tags = resource.get_tags()
            if tags is not None:
                r["Properties"]["Tags"] = []
                for (key, value) in tags.items():
                    r["Properties"]["Tags"].append({"Key": key, "Value": value})

            response[resource.get_logical_id()] = r

        return response
