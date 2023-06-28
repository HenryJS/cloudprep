from ..AwsElement import AwsElement
from ..TagSet import TagSet


class RouteTarget(AwsElement):
    def __init__(self, tag, environment, physical_id, **kwargs):
        super().__init__(environment, tag, physical_id, **kwargs)
        if "route" not in kwargs:
            raise Exception("Route not specified for RouteTarget " + physical_id)

        self._route = kwargs["route"]
        self._tags = TagSet()

    @AwsElement.capture_method
    def capture(self):
        self._route = None
        raise NotImplementedError("capture is not implemented in this class.")
