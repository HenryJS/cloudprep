from .AwsInternetGateway import AwsInternetGateway
from .AwsVpcEndpoint import AwsVPCEndpoint
from .AwsEgressOnlyInternetGateway import AwsEgressOnlyInternetGateway
from .AwsNatGateway import AwsNatGateway
from .AwsTransitGateway import AwsTransitGateway


class RouteTargetBuilder:

    TARGET_ASSOC = {
            "igw": AwsInternetGateway,
            "vpce": AwsVPCEndpoint,
            "local": None,
            "nat": AwsNatGateway,
            "eigw": AwsEgressOnlyInternetGateway,
            "tgw": AwsTransitGateway,
    }

    @staticmethod
    def find_route_target(prefix, **kwargs):
        if prefix not in RouteTargetBuilder.TARGET_ASSOC:
            raise NotImplementedError(prefix + " is not a supported route target.")

        if RouteTargetBuilder.TARGET_ASSOC[prefix] is None:
            return None

        return RouteTargetBuilder.TARGET_ASSOC[prefix](**kwargs)

