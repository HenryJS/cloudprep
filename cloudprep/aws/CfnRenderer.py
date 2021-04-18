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
                "Outputs" : env.outputs
            }, indent=4
        ))


    def renderResources(self, resourceSet):
        response = {}
        for resource in resourceSet:
            if not resource.isValid():
                continue

            r = { "Type": resource.getType(),
                  "Properties": {}}

            for (property,value) in resource.getProperties().items():
                if not resource.isDefault(property):
                    r["Properties"][property] = value

            tags = resource.getTags()
            if tags is not None:
                r["Properties"]["Tags"] = []
                for (key, value) in tags.items():
                    r["Properties"]["Tags"].append({"Key": key, "Value": value})

            response[resource.getLogicalId()] = r

        return response