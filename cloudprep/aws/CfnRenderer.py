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
                if not resource.isDefault(property):
                    r["Properties"][property] = resource._element[property]
            if resource._tags is not None:
                r["Properties"]["Tags"] = resource._tags.toCfn()
            response[resource.getLogicalId()] = r

        return response