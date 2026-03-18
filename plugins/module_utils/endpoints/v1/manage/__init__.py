from __future__ import absolute_import, division, print_function

from ansible_collections.cisco.nd.plugins.module_utils.endpoints.v1.manage.manage_fabrics_switches_vpc_pair import (
    EpVpcPairGet,
    EpVpcPairPut,
)
from ansible_collections.cisco.nd.plugins.module_utils.endpoints.v1.manage.manage_fabrics_switches_vpc_pair_support import (
    EpVpcPairSupportGet,
)
from ansible_collections.cisco.nd.plugins.module_utils.endpoints.v1.manage.manage_fabrics_switches_vpc_pair_overview import (
    EpVpcPairOverviewGet,
)
from ansible_collections.cisco.nd.plugins.module_utils.endpoints.v1.manage.manage_fabrics_switches_vpc_pair_recommendation import (
    EpVpcPairRecommendationGet,
)
from ansible_collections.cisco.nd.plugins.module_utils.endpoints.v1.manage.manage_fabrics_switches_vpc_pair_consistency import (
    EpVpcPairConsistencyGet,
)
from ansible_collections.cisco.nd.plugins.module_utils.endpoints.v1.manage.manage_fabrics_vpc_pairs import (
    EpVpcPairsListGet,
)

__all__ = [
    "EpVpcPairGet",
    "EpVpcPairPut",
    "EpVpcPairSupportGet",
    "EpVpcPairOverviewGet",
    "EpVpcPairRecommendationGet",
    "EpVpcPairConsistencyGet",
    "EpVpcPairsListGet",
]
