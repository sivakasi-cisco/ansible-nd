from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.cisco.nd.plugins.module_utils.ep.v1 import (
    EpVpcPairConsistencyGet,
    EpVpcPairGet,
    EpVpcPairOverviewGet,
    EpVpcPairPut,
    EpVpcPairRecommendationGet,
    EpVpcPairSupportGet,
    EpVpcPairsListGet,
    VpcPairBasePath,
)

__all__ = [
    "VpcPairBasePath",
    "EpVpcPairGet",
    "EpVpcPairPut",
    "EpVpcPairSupportGet",
    "EpVpcPairOverviewGet",
    "EpVpcPairRecommendationGet",
    "EpVpcPairConsistencyGet",
    "EpVpcPairsListGet",
]
