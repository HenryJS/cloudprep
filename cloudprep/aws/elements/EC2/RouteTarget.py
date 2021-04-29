from ..AwsElement import AwsElement
from ..TagSet import TagSet


class RouteTarget(AwsElement):
    def __init__(self, tag, environment, physical_id, route):
        super().__init__(environment, tag, physical_id)
        self._route = route
        self._tags = TagSet({"CreatedBy": "CloudPrep"})

    @AwsElement.capture_method
    def capture(self):
        self._route = None
        raise NotImplementedError("capture is not implemented in this class.")
