import json


class CfnRenderer:
    def __init__(self):
        pass

    def render(self, env):
        print(json.dumps(
            {
                "Description": env.description,
                "Mappings": env.mappings,
                "Resources": self.renderResources(env.resources),
                "Outputs": env.outputs
            }, indent=4
        ))

    def renderResources(self, resourceSet):
        response = {}
        for resource in resourceSet:
            if not resource.isValid():
                continue

            r = {
                "Type": resource.getType(),
                "Properties": {}
            }

            for (prop, value) in resource.getProperties().items():
                if not resource.isDefault(prop):
                    r["Properties"][prop] = value

            tags = resource.get_tags()
            if tags is not None:
                r["Properties"]["Tags"] = []
                for (key, value) in tags.items():
                    r["Properties"]["Tags"].append({"Key": key, "Value": value})

            response[resource.getLogicalId()] = r

        return response
