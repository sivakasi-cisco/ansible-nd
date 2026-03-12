# Copyright (c) 2026 Cisco and/or its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Centralized base paths for VPC pair API endpoints.

This module provides a single location to manage all VPC pair API base paths,
allowing easy modification when API paths change. All endpoint classes
should use these path builders for consistency.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type
__author__ = "Sivakami Sivaraman"

from typing import Final

from ansible_collections.cisco.nd.plugins.module_utils.endpoints.base_path import (
    ApiPath,
)
from ansible_collections.cisco.nd.plugins.module_utils.vpc_pair.common import (
    build_path,
    require_non_empty_str,
)


class VpcPairBasePath:
    """
    # Summary

    Centralized VPC Pair API Base Paths

    ## Description

    Provides centralized base path definitions for all ND Manage VPC Pair
    API endpoints. This allows API path changes to be managed in a single
    location.

    ## Usage

    ```python
    # Get VPC pair details path
    path = VpcPairBasePath.vpc_pair("Fabric1", "FDO23040Q85")
    # Returns: /api/v1/manage/fabrics/Fabric1/switches/FDO23040Q85/vpcPair

    # Get VPC pairs list path
    path = VpcPairBasePath.vpc_pairs_list("Fabric1")
    # Returns: /api/v1/manage/fabrics/Fabric1/vpcPairs
    ```

    ## Design Notes

    - All base paths are defined as class constants for easy modification
    - Helper methods compose paths from base constants
    - Use these methods in Pydantic endpoint models to ensure consistency
    - If ND changes base API paths, only this class needs updating
    """

    # Root API paths
    MANAGE_API: Final = ApiPath.MANAGE.value

    @classmethod
    def manage(cls, *segments: str) -> str:
        """
        # Summary

        Build path from Manage API root.

        ## Parameters

        - segments: Path segments to append

        ## Returns

        - Complete path string

        ## Example

        ```python
        path = VpcPairBasePath.manage("fabrics", "Fabric1")
        # Returns: /api/v1/manage/fabrics/Fabric1
        ```
        """
        return build_path(cls.MANAGE_API, *segments)

    @classmethod
    def fabrics(cls, fabric_name: str, *segments: str) -> str:
        """
        # Summary

        Build fabrics API path.

        ## Parameters

        - fabric_name: Name of the fabric
        - segments: Additional path segments to append

        ## Returns

        - Complete fabrics path

        ## Raises

        - ValueError: If fabric_name is None, empty, or not a string

        ## Example

        ```python
        path = VpcPairBasePath.fabrics("Fabric1", "switches")
        # Returns: /api/v1/manage/fabrics/Fabric1/switches
        ```
        """
        fabric_name = require_non_empty_str(
            name="fabric_name",
            value=fabric_name,
            owner="VpcPairBasePath.fabrics()",
        )
        
        return cls.manage("fabrics", fabric_name, *segments)

    @classmethod
    def switches(cls, fabric_name: str, switch_id: str, *segments: str) -> str:
        """
        # Summary

        Build switches API path.

        ## Parameters

        - fabric_name: Name of the fabric
        - switch_id: Serial number of the switch
        - segments: Additional path segments to append

        ## Returns

        - Complete switches path

        ## Example

        ```python
        path = VpcPairBasePath.switches("Fabric1", "FDO23040Q85")
        # Returns: /api/v1/manage/fabrics/Fabric1/switches/FDO23040Q85
        ```
        """
        if not segments:
            return cls.fabrics(fabric_name, "switches", switch_id)
        return cls.fabrics(fabric_name, "switches", switch_id, *segments)

    @classmethod
    def vpc_pair(cls, fabric_name: str, switch_id: str) -> str:
        """
        # Summary

        Build VPC pair details API path.

        ## Parameters

        - fabric_name: Name of the fabric
        - switch_id: Serial number of the switch

        ## Returns

        - Complete VPC pair path

        ## Example

        ```python
        path = VpcPairBasePath.vpc_pair("Fabric1", "FDO23040Q85")
        # Returns: /api/v1/manage/fabrics/Fabric1/switches/FDO23040Q85/vpcPair
        ```
        """
        return cls.switches(fabric_name, switch_id, "vpcPair")

    @classmethod
    def vpc_pair_support(cls, fabric_name: str, switch_id: str) -> str:
        """
        # Summary

        Build VPC pair support check API path.

        ## Parameters

        - fabric_name: Name of the fabric
        - switch_id: Serial number of the switch

        ## Returns

        - Complete VPC pair support path

        ## Example

        ```python
        path = VpcPairBasePath.vpc_pair_support("Fabric1", "FDO23040Q85")
        # Returns: /api/v1/manage/fabrics/Fabric1/switches/FDO23040Q85/vpcPairSupport
        ```
        """
        return cls.switches(fabric_name, switch_id, "vpcPairSupport")

    @classmethod
    def vpc_pair_overview(cls, fabric_name: str, switch_id: str) -> str:
        """
        # Summary

        Build VPC pair overview API path.

        ## Parameters

        - fabric_name: Name of the fabric
        - switch_id: Serial number of the switch

        ## Returns

        - Complete VPC pair overview path

        ## Example

        ```python
        path = VpcPairBasePath.vpc_pair_overview("Fabric1", "FDO23040Q85")
        # Returns: /api/v1/manage/fabrics/Fabric1/switches/FDO23040Q85/vpcPairOverview
        ```
        """
        return cls.switches(fabric_name, switch_id, "vpcPairOverview")

    @classmethod
    def vpc_pair_recommendation(cls, fabric_name: str, switch_id: str) -> str:
        """
        # Summary

        Build VPC pair recommendation API path.

        ## Parameters

        - fabric_name: Name of the fabric
        - switch_id: Serial number of the switch

        ## Returns

        - Complete VPC pair recommendation path

        ## Example

        ```python
        path = VpcPairBasePath.vpc_pair_recommendation("Fabric1", "FDO23040Q85")
        # Returns: /api/v1/manage/fabrics/Fabric1/switches/FDO23040Q85/vpcPairRecommendation
        ```
        """
        return cls.switches(fabric_name, switch_id, "vpcPairRecommendation")

    @classmethod
    def vpc_pair_consistency(cls, fabric_name: str, switch_id: str) -> str:
        """
        # Summary

        Build VPC pair consistency API path.

        ## Parameters

        - fabric_name: Name of the fabric
        - switch_id: Serial number of the switch

        ## Returns

        - Complete VPC pair consistency path

        ## Example

        ```python
        path = VpcPairBasePath.vpc_pair_consistency("Fabric1", "FDO23040Q85")
        # Returns: /api/v1/manage/fabrics/Fabric1/switches/FDO23040Q85/vpcPairConsistency
        ```
        """
        return cls.switches(fabric_name, switch_id, "vpcPairConsistency")

    @classmethod
    def vpc_pairs_list(cls, fabric_name: str) -> str:
        """
        # Summary

        Build VPC pairs list API path.

        ## Parameters

        - fabric_name: Name of the fabric

        ## Returns

        - Complete VPC pairs list path

        ## Example

        ```python
        path = VpcPairBasePath.vpc_pairs_list("Fabric1")
        # Returns: /api/v1/manage/fabrics/Fabric1/vpcPairs
        ```
        """
        return cls.fabrics(fabric_name, "vpcPairs")
