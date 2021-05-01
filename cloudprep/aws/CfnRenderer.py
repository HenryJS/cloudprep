import json
import sys


class CfnRenderer:
    def __init__(self, environment):
        self._environment = environment

    def render(self):
        print(json.dumps(
            {
                "Parameters": self._environment.parameters,
                "Description": self._environment.description,
                "Mappings": self._environment.mappings,
                "Resources": self.render_resources(self._environment.resources),
                "Outputs": self._environment.outputs
            }, indent=4
        ))

    @staticmethod
    def render_resources(resource_set):
        response = {}
        print("Rendering CFN.", file=sys.stderr)
        for physical_id, resource in resource_set.items():
            if not resource.is_valid:
                # print(resource.logical_id, "is not valid.", file=sys.stderr)
                continue

            r = {
                "Type": resource.type,
                "Properties": {}
            }

            if len(resource.dependencies) > 0:
                r["DependsOn"] = []
                for dep in resource.dependencies:
                    r["DependsOn"].append(dep)

            for (prop, value) in resource.properties.items():
                if not resource.is_default(prop):
                    r["Properties"][prop] = value

            tags = resource.tags
            if tags is not None:
                r["Properties"]["Tags"] = []
                for (key, value) in tags.items():
                    r["Properties"]["Tags"].append({"Key": key, "Value": value})

            response[resource.logical_id] = r

        return response
