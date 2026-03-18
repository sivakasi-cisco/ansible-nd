# -*- coding: utf-8 -*-
#
# Copyright: (c) 2026, Sivakami Sivaraman sivakasi@cisco.com
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

"""
vPC endpoint export map.

Class -> API path:
- EpVpcPairGet / EpVpcPairPut -> /api/v1/manage/fabrics/{fabricName}/switches/{switchId}/vpcPair
- EpVpcPairSupportGet -> /api/v1/manage/fabrics/{fabricName}/switches/{switchId}/vpcPairSupport
- EpVpcPairOverviewGet -> /api/v1/manage/fabrics/{fabricName}/switches/{switchId}/vpcPairOverview
- EpVpcPairRecommendationGet -> /api/v1/manage/fabrics/{fabricName}/switches/{switchId}/vpcPairRecommendation
- EpVpcPairConsistencyGet -> /api/v1/manage/fabrics/{fabricName}/switches/{switchId}/vpcPairConsistency
- EpVpcPairsListGet -> /api/v1/manage/fabrics/{fabricName}/vpcPairs
"""

# Backward-compatible export surface for legacy imports.
from ansible_collections.cisco.nd.plugins.module_utils.endpoints.v1.manage.manage_fabrics_switches_vpc_pair import (
    EpVpcPairGet,
    EpVpcPairPut,
)
from ansible_collections.cisco.nd.plugins.module_utils.endpoints.v1.manage.manage_fabrics_switches_vpc_pair_consistency import (
    EpVpcPairConsistencyGet,
)
from ansible_collections.cisco.nd.plugins.module_utils.endpoints.v1.manage.manage_fabrics_switches_vpc_pair_overview import (
    EpVpcPairOverviewGet,
)
from ansible_collections.cisco.nd.plugins.module_utils.endpoints.v1.manage.manage_fabrics_switches_vpc_pair_recommendation import (
    EpVpcPairRecommendationGet,
)
from ansible_collections.cisco.nd.plugins.module_utils.endpoints.v1.manage.manage_fabrics_switches_vpc_pair_support import (
    EpVpcPairSupportGet,
)
from ansible_collections.cisco.nd.plugins.module_utils.endpoints.v1.manage.manage_fabrics_vpc_pairs import (
    EpVpcPairsListGet,
)
from ansible_collections.cisco.nd.plugins.module_utils.endpoints.v1.manage.vpc_pair_base_paths import (
    VpcPairBasePath,
)

__all__ = [
    "EpVpcPairGet",
    "EpVpcPairPut",
    "EpVpcPairSupportGet",
    "EpVpcPairOverviewGet",
    "EpVpcPairRecommendationGet",
    "EpVpcPairConsistencyGet",
    "EpVpcPairsListGet",
    "VpcPairBasePath",
]
