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
VPC Pair endpoint models.

This module contains endpoint definitions for VPC pair management operations
in the ND Manage API.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type
__author__ = "Sivakami Sivaraman"

from typing import TYPE_CHECKING, Literal, Optional

from ansible_collections.cisco.nd.plugins.module_utils.manage.vpc_pair.base_paths import VpcPairBasePath
from ansible_collections.cisco.nd.plugins.module_utils.manage.vpc_pair.endpoint_mixins import (
    ComponentTypeMixin,
    FabricNameMixin,
    FilterMixin,
    FromClusterMixin,
    PaginationMixin,
    SortMixin,
    SwitchIdMixin,
    TicketIdMixin,
    ViewMixin,
)
from ansible_collections.cisco.nd.plugins.module_utils.manage.vpc_pair.enums import VerbEnum

if TYPE_CHECKING:
    from pydantic import BaseModel, ConfigDict, Field
else:
    try:
        from pydantic import BaseModel, ConfigDict, Field
    except ImportError:
        # Fallback for environments without pydantic
        class BaseModel:
            pass

        def ConfigDict(*args, **kwargs):
            return {}

        def Field(*args, **kwargs):
            return None


# Common config for basic validation
COMMON_CONFIG = ConfigDict(validate_assignment=True)


# ============================================================================
# VPC Pair Details Endpoints (/vpcPair)
# ============================================================================


class _EpVpcPairBase(FabricNameMixin, SwitchIdMixin, FromClusterMixin, BaseModel):
    """
    Base class for VPC pair details endpoints.

    Provides common functionality for all HTTP methods on the
    /fabrics/{fabricName}/switches/{switchId}/vpcPair endpoint.
    """

    model_config = COMMON_CONFIG

    @property
    def path(self) -> str:
        """
        # Summary

        Build the endpoint path.

        ## Returns

        - Complete endpoint path string
        """
        if self.fabric_name is None or self.switch_id is None:
            raise ValueError("fabric_name and switch_id are required")
        return VpcPairBasePath.vpc_pair(self.fabric_name, self.switch_id)


class EpVpcPairGet(_EpVpcPairBase):
    """
    # Summary

    VPC Pair Details GET Endpoint

    ## Description

    Endpoint to retrieve VPC pair details for a specific switch.

    ## Path

    - /api/v1/manage/fabrics/{fabricName}/switches/{switchId}/vpcPair

    ## Verb

    - GET

    ## Usage

    ```python
    # Get VPC pair details
    endpoint = EpVpcPairGet()
    endpoint.fabric_name = "Fabric1"
    endpoint.switch_id = "FDO23040Q85"
    endpoint.from_cluster = "cluster1"  # Optional
    path = endpoint.path
    verb = endpoint.verb
    ```
    """

    class_name: Literal["EpVpcPairGet"] = Field(default="EpVpcPairGet", description="Class name for backward compatibility")

    @property
    def verb(self) -> VerbEnum:
        """Return the HTTP verb for this endpoint."""
        return VerbEnum.GET


class EpVpcPairPut(_EpVpcPairBase, TicketIdMixin):
    """
    # Summary

    VPC Pair Management PUT Endpoint

    ## Description

    Endpoint to manage (create, update, delete) VPC pair configuration.
    Use vpcAction="pair" for pairing and vpcAction="unPair" for unpairing.

    ## Path

    - /api/v1/manage/fabrics/{fabricName}/switches/{switchId}/vpcPair

    ## Verb

    - PUT

    ## Usage

    ```python
    # Manage VPC pair
    endpoint = EpVpcPairPut()
    endpoint.fabric_name = "Fabric1"
    endpoint.switch_id = "FDO23040Q85"
    endpoint.ticket_id = "CHG001"  # Optional
    path = endpoint.path
    verb = endpoint.verb
    ```
    """

    class_name: Literal["EpVpcPairPut"] = Field(default="EpVpcPairPut", description="Class name for backward compatibility")

    @property
    def verb(self) -> VerbEnum:
        """Return the HTTP verb for this endpoint."""
        return VerbEnum.PUT


# ============================================================================
# VPC Pair Support Endpoints (/vpcPairSupport)
# ============================================================================


class EpVpcPairSupportGet(FabricNameMixin, SwitchIdMixin, FromClusterMixin, ComponentTypeMixin, BaseModel):
    """
    # Summary

    VPC Pair Support Check GET Endpoint

    ## Description

    Endpoint to check VPC pairing support and validation details.
    Supports componentType="checkPairing" or "checkFabricPeeringSupport".

    ## Path

    - /api/v1/manage/fabrics/{fabricName}/switches/{switchId}/vpcPairSupport

    ## Verb

    - GET

    ## Query Parameters

    - componentType: Required. Values: "checkPairing", "checkFabricPeeringSupport"

    ## Usage

    ```python
    # Check if pairing is allowed
    endpoint = EpVpcPairSupportGet()
    endpoint.fabric_name = "Fabric1"
    endpoint.switch_id = "FDO23040Q85"
    endpoint.component_type = "checkPairing"
    path = endpoint.path
    verb = endpoint.verb
    ```
    """

    model_config = COMMON_CONFIG
    class_name: Literal["EpVpcPairSupportGet"] = Field(default="EpVpcPairSupportGet", description="Class name for backward compatibility")

    @property
    def path(self) -> str:
        """Build the endpoint path."""
        if self.fabric_name is None or self.switch_id is None:
            raise ValueError("fabric_name and switch_id are required")
        return VpcPairBasePath.vpc_pair_support(self.fabric_name, self.switch_id)

    @property
    def verb(self) -> VerbEnum:
        """Return the HTTP verb for this endpoint."""
        return VerbEnum.GET


# ============================================================================
# VPC Pair Overview Endpoints (/vpcPairOverview)
# ============================================================================


class EpVpcPairOverviewGet(FabricNameMixin, SwitchIdMixin, FromClusterMixin, ComponentTypeMixin, BaseModel):
    """
    # Summary

    VPC Pair Overview GET Endpoint

    ## Description

    Endpoint to retrieve VPC pair overview details with various component types.

    ## Path

    - /api/v1/manage/fabrics/{fabricName}/switches/{switchId}/vpcPairOverview

    ## Verb

    - GET

    ## Query Parameters

    - componentType: Required. Values: "full", "health", "module", "vxlan",
      "overlay", "pairsInfo", "inventory", "anomalies"

    ## Usage

    ```python
    # Get full overview
    endpoint = EpVpcPairOverviewGet()
    endpoint.fabric_name = "Fabric1"
    endpoint.switch_id = "FDO23040Q85"
    endpoint.component_type = "full"
    path = endpoint.path
    verb = endpoint.verb
    ```
    """

    model_config = COMMON_CONFIG
    class_name: Literal["EpVpcPairOverviewGet"] = Field(default="EpVpcPairOverviewGet", description="Class name for backward compatibility")

    @property
    def path(self) -> str:
        """Build the endpoint path."""
        if self.fabric_name is None or self.switch_id is None:
            raise ValueError("fabric_name and switch_id are required")
        return VpcPairBasePath.vpc_pair_overview(self.fabric_name, self.switch_id)

    @property
    def verb(self) -> VerbEnum:
        """Return the HTTP verb for this endpoint."""
        return VerbEnum.GET


# ============================================================================
# VPC Pair Recommendation Endpoints (/vpcPairRecommendation)
# ============================================================================


class EpVpcPairRecommendationGet(FabricNameMixin, SwitchIdMixin, FromClusterMixin, BaseModel):
    """
    # Summary

    VPC Pair Recommendation GET Endpoint

    ## Description

    Endpoint to get recommendations for VPC pairing with available devices.

    ## Path

    - /api/v1/manage/fabrics/{fabricName}/switches/{switchId}/vpcPairRecommendation

    ## Verb

    - GET

    ## Query Parameters

    - useVirtualPeerLink: Optional boolean

    ## Usage

    ```python
    # Get pairing recommendations
    endpoint = EpVpcPairRecommendationGet()
    endpoint.fabric_name = "Fabric1"
    endpoint.switch_id = "FDO23040Q85"
    endpoint.use_virtual_peer_link = True
    path = endpoint.path
    verb = endpoint.verb
    ```
    """

    model_config = COMMON_CONFIG
    class_name: Literal["EpVpcPairRecommendationGet"] = Field(default="EpVpcPairRecommendationGet", description="Class name for backward compatibility")

    use_virtual_peer_link: Optional[bool] = Field(default=None, description="Virtual peer link available")

    @property
    def path(self) -> str:
        """Build the endpoint path."""
        if self.fabric_name is None or self.switch_id is None:
            raise ValueError("fabric_name and switch_id are required")
        return VpcPairBasePath.vpc_pair_recommendation(self.fabric_name, self.switch_id)

    @property
    def verb(self) -> VerbEnum:
        """Return the HTTP verb for this endpoint."""
        return VerbEnum.GET


# ============================================================================
# VPC Pair Consistency Endpoints (/vpcPairConsistency)
# ============================================================================


class EpVpcPairConsistencyGet(FabricNameMixin, SwitchIdMixin, FromClusterMixin, BaseModel):
    """
    # Summary

    VPC Pair Consistency GET Endpoint

    ## Description

    Endpoint to retrieve VPC pair consistency details between peers.

    ## Path

    - /api/v1/manage/fabrics/{fabricName}/switches/{switchId}/vpcPairConsistency

    ## Verb

    - GET

    ## Usage

    ```python
    # Get consistency details
    endpoint = EpVpcPairConsistencyGet()
    endpoint.fabric_name = "Fabric1"
    endpoint.switch_id = "FDO23040Q85"
    path = endpoint.path
    verb = endpoint.verb
    ```
    """

    model_config = COMMON_CONFIG
    class_name: Literal["EpVpcPairConsistencyGet"] = Field(default="EpVpcPairConsistencyGet", description="Class name for backward compatibility")

    @property
    def path(self) -> str:
        """Build the endpoint path."""
        if self.fabric_name is None or self.switch_id is None:
            raise ValueError("fabric_name and switch_id are required")
        return VpcPairBasePath.vpc_pair_consistency(self.fabric_name, self.switch_id)

    @property
    def verb(self) -> VerbEnum:
        """Return the HTTP verb for this endpoint."""
        return VerbEnum.GET


# ============================================================================
# VPC Pairs List Endpoints (/vpcPairs)
# ============================================================================


class EpVpcPairsListGet(FabricNameMixin, FromClusterMixin, FilterMixin, PaginationMixin, SortMixin, ViewMixin, BaseModel):
    """
    # Summary

    VPC Pairs List GET Endpoint

    ## Description

    Endpoint to list all VPC pairs for a specific fabric.
    Supports filtering, pagination, and sorting.

    ## Path

    - /api/v1/manage/fabrics/{fabricName}/vpcPairs

    ## Verb

    - GET

    ## Query Parameters

    - filter: Optional filter expression
    - max: Optional maximum number of results
    - offset: Optional offset for pagination
    - sort: Optional sort field
    - view: Optional. Values: "intendedPairs"

    ## Usage

    ```python
    # List VPC pairs with filtering
    endpoint = EpVpcPairsListGet()
    endpoint.fabric_name = "Fabric1"
    endpoint.filter = "domainId:10"
    endpoint.max = 50
    endpoint.offset = 0
    endpoint.sort = "switchName:asc"
    endpoint.view = "intendedPairs"
    path = endpoint.path
    verb = endpoint.verb
    ```
    """

    model_config = COMMON_CONFIG
    class_name: Literal["EpVpcPairsListGet"] = Field(default="EpVpcPairsListGet", description="Class name for backward compatibility")

    @property
    def path(self) -> str:
        """Build the endpoint path."""
        if self.fabric_name is None:
            raise ValueError("fabric_name is required")
        return VpcPairBasePath.vpc_pairs_list(self.fabric_name)

    @property
    def verb(self) -> VerbEnum:
        """Return the HTTP verb for this endpoint."""
        return VerbEnum.GET
