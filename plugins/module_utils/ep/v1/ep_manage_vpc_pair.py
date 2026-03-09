# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Sivakami S <sivakasi@cisco.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.cisco.nd.plugins.module_utils.manage.vpc_pair.base_paths import (
    VpcPairBasePath,
)
from ansible_collections.cisco.nd.plugins.module_utils.manage.vpc_pair.vpc_pair_endpoints import (
    EpVpcPairConsistencyGet,
    EpVpcPairGet,
    EpVpcPairOverviewGet,
    EpVpcPairPut,
    EpVpcPairRecommendationGet,
    EpVpcPairSupportGet,
    EpVpcPairsListGet,
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
