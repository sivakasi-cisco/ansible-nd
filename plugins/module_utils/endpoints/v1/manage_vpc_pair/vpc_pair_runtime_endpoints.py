# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Sivakami S <sivakasi@cisco.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

from typing import Optional

from ansible_collections.cisco.nd.plugins.module_utils.endpoints.query_params import (
    CompositeQueryParams,
    EndpointQueryParams,
)
from ansible_collections.cisco.nd.plugins.module_utils.endpoints.v1.manage_vpc_pair.enums import (
    ComponentTypeSupportEnum,
)

try:
    from ansible_collections.cisco.nd.plugins.module_utils.endpoints.v1.manage_vpc_pair.vpc_pair_endpoints import (
        EpVpcPairConsistencyGet,
        EpVpcPairGet,
        EpVpcPairPut,
        EpVpcPairOverviewGet,
        EpVpcPairRecommendationGet,
        EpVpcPairSupportGet,
        EpVpcPairsListGet,
        VpcPairBasePath,
    )
except ImportError:
    from ansible_collections.cisco.nd.plugins.module_utils.endpoints.v1.manage_vpc_pair import (
        EpVpcPairConsistencyGet,
        EpVpcPairGet,
        EpVpcPairPut,
        EpVpcPairOverviewGet,
        EpVpcPairRecommendationGet,
        EpVpcPairSupportGet,
        EpVpcPairsListGet,
        VpcPairBasePath,
    )


class _ComponentTypeQueryParams(EndpointQueryParams):
    """Query params for endpoints that require componentType."""

    component_type: Optional[str] = None


class _ForceShowRunQueryParams(EndpointQueryParams):
    """Query params for deploy endpoint."""

    force_show_run: Optional[bool] = None


class VpcPairEndpoints:
    """Centralized endpoint builders for vPC pair runtime operations."""

    NDFC_BASE = "/appcenter/cisco/ndfc/api/v1/lan-fabric/rest"
    MANAGE_BASE = "/api/v1/manage"
    VPC_PAIR_BASE = f"{NDFC_BASE}/vpcpair/fabrics/{{fabric_name}}"
    VPC_PAIR_SWITCH = f"{NDFC_BASE}/vpcpair/fabrics/{{fabric_name}}/switches/{{switch_id}}"
    FABRIC_CONFIG_SAVE = f"{MANAGE_BASE}/fabrics/{{fabric_name}}/actions/configSave"
    FABRIC_CONFIG_DEPLOY = f"{MANAGE_BASE}/fabrics/{{fabric_name}}/actions/deploy"
    FABRIC_SWITCHES = f"{MANAGE_BASE}/fabrics/{{fabric_name}}/switches"
    SWITCH_VPC_PAIR = f"{MANAGE_BASE}/fabrics/{{fabric_name}}/switches/{{switch_id}}/vpcPair"
    SWITCH_VPC_RECOMMENDATIONS = (
        f"{MANAGE_BASE}/fabrics/{{fabric_name}}/switches/{{switch_id}}/vpcPairRecommendation"
    )
    SWITCH_VPC_OVERVIEW = f"{MANAGE_BASE}/fabrics/{{fabric_name}}/switches/{{switch_id}}/vpcPairOverview"

    @staticmethod
    def _append_query(path: str, *query_groups: EndpointQueryParams) -> str:
        composite_params = CompositeQueryParams()
        for query_group in query_groups:
            composite_params.add(query_group)
        query_string = composite_params.to_query_string(url_encode=False)
        return f"{path}?{query_string}" if query_string else path

    @staticmethod
    def vpc_pair_base(fabric_name: str) -> str:
        endpoint = EpVpcPairsListGet(fabric_name=fabric_name)
        return endpoint.path

    @staticmethod
    def vpc_pairs_list(fabric_name: str) -> str:
        endpoint = EpVpcPairsListGet(fabric_name=fabric_name)
        return endpoint.path

    @staticmethod
    def vpc_pair_put(fabric_name: str, switch_id: str) -> str:
        endpoint = EpVpcPairPut(fabric_name=fabric_name, switch_id=switch_id)
        return endpoint.path

    @staticmethod
    def fabric_switches(fabric_name: str) -> str:
        return VpcPairBasePath.fabrics(fabric_name, "switches")

    @staticmethod
    def switch_vpc_pair(fabric_name: str, switch_id: str) -> str:
        endpoint = EpVpcPairGet(fabric_name=fabric_name, switch_id=switch_id)
        return endpoint.path

    @staticmethod
    def switch_vpc_recommendations(fabric_name: str, switch_id: str) -> str:
        endpoint = EpVpcPairRecommendationGet(fabric_name=fabric_name, switch_id=switch_id)
        return endpoint.path

    @staticmethod
    def switch_vpc_overview(fabric_name: str, switch_id: str, component_type: str = "full") -> str:
        endpoint = EpVpcPairOverviewGet(fabric_name=fabric_name, switch_id=switch_id)
        base_path = endpoint.path
        query_params = _ComponentTypeQueryParams(component_type=component_type)
        return VpcPairEndpoints._append_query(base_path, query_params)

    @staticmethod
    def switch_vpc_support(
        fabric_name: str,
        switch_id: str,
        component_type: str = ComponentTypeSupportEnum.CHECK_PAIRING.value,
    ) -> str:
        endpoint = EpVpcPairSupportGet(
            fabric_name=fabric_name,
            switch_id=switch_id,
            component_type=component_type,
        )
        base_path = endpoint.path
        query_params = _ComponentTypeQueryParams(component_type=component_type)
        return VpcPairEndpoints._append_query(base_path, query_params)

    @staticmethod
    def switch_vpc_consistency(fabric_name: str, switch_id: str) -> str:
        endpoint = EpVpcPairConsistencyGet(fabric_name=fabric_name, switch_id=switch_id)
        return endpoint.path

    @staticmethod
    def fabric_config_save(fabric_name: str) -> str:
        return VpcPairBasePath.fabrics(fabric_name, "actions", "configSave")

    @staticmethod
    def fabric_config_deploy(fabric_name: str, force_show_run: bool = True) -> str:
        base_path = VpcPairBasePath.fabrics(fabric_name, "actions", "deploy")
        query_params = _ForceShowRunQueryParams(
            force_show_run=True if force_show_run else None
        )
        return VpcPairEndpoints._append_query(base_path, query_params)
