# TODO:
#  * Ensure that elements can't be processed multiple times.

class AwsEnvironment:
    def __init__(self):
        self.description = "AWS Environment generated by CloudPrep"
        self.resources = []
        self.parameters = {}
        self.outputs = {}
        self.mappings = {}

        self._todo = []

    def findByPhysicalId(self, needle):
        for r in self.resources:
            if r.getPhysicalId() == needle:
                return r
        return None

    def logicalFromPhysical(self, needle):
        return self.findByPhysicalId(needle).getLogicalId()

    def addToTodo(self, element):
        self._todo.append(element)

    def getNextTodo(self):
        if len(self._todo) > 0:
            return self._todo[0]
        else:
            return None

    def removeFromTodo(self, task):
        self._todo.remove(task)

    def add_intermediate_resource(self, resource):
        self.resources.append(resource)
