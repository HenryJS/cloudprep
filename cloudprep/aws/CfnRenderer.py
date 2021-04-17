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
            r = { "Type": resource.getType(),
                  "Properties": {}}
            for property in resource._element:
                r["Properties"][property] = resource._element[property]
            response[resource.getLogicalId()] = r

        return response