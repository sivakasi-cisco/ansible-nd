from __future__ import absolute_import, division, print_function

__metaclass__ = type
__copyright__ = "Copyright (c) 2026 Cisco and/or its affiliates."
__author__ = "Neil John"

"""
VPC pair management utilities for Cisco ND Ansible collection.

This package provides Pydantic-based schemas and endpoint models for
managing VPC pairs in Nexus Dashboard.

Components:
- enums: Enumeration types for constrained values
- mixins: Reusable field mixins for composition
- base_paths: Centralized API path builders
- vpc_pair_endpoints: Endpoint models for each API operation
- vpc_pair_schemas: Request/response data schemas

Usage:
    from ansible_collections.cisco.nd.plugins.module_utils.manage.vpc_pair import (
        EpVpcPairGet,
        EpVpcPairPut,
        VpcPairDetailsDefault,
        VpcPairingRequest,
        VpcActionEnum,
    )
"""

# Export commonly used components for easier imports
__all__ = [
    # Endpoints
    "EpVpcPairGet",
    "EpVpcPairPut",
    "EpVpcPairSupportGet",
    "EpVpcPairOverviewGet",
    "EpVpcPairRecommendationGet",
    "EpVpcPairConsistencyGet",
    "EpVpcPairsListGet",
    # Schemas
    "VpcPairDetailsDefault",
    "VpcPairDetailsCustom",
    "VpcPairingRequest",
    "VpcUnpairingRequest",
    "VpcPairBase",
    "VpcPairConsistency",
    "VpcPairRecommendation",
    # Enums
    "VerbEnum",
    "VpcActionEnum",
    "VpcPairTypeEnum",
    "KeepAliveVrfEnum",
    "PoModeEnum",
    "PortChannelDuplexEnum",
    "VpcRoleEnum",
    "MaintenanceModeEnum",
    "ComponentTypeOverviewEnum",
    "ComponentTypeSupportEnum",
    "VpcPairViewEnum",
    # Field names
    "VpcFieldNames",
    # Base paths
    "VpcPairBasePath",
]

# Try to import and expose components (graceful fallback if pydantic not available)
try:
    from ansible_collections.cisco.nd.plugins.module_utils.manage.vpc_pair.vpc_pair_endpoints import (
        EpVpcPairGet,
        EpVpcPairPut,
        EpVpcPairSupportGet,
        EpVpcPairOverviewGet,
        EpVpcPairRecommendationGet,
        EpVpcPairConsistencyGet,
        EpVpcPairsListGet,
    )
    from ansible_collections.cisco.nd.plugins.module_utils.manage.vpc_pair.model_playbook_vpc_pair import (
        VpcPairDetailsDefault,
        VpcPairDetailsCustom,
        VpcPairingRequest,
        VpcUnpairingRequest,
        VpcPairBase,
        VpcPairConsistency,
        VpcPairRecommendation,
    )
    from ansible_collections.cisco.nd.plugins.module_utils.manage.vpc_pair.enums import (
        VerbEnum,
        VpcActionEnum,
        VpcPairTypeEnum,
        KeepAliveVrfEnum,
        PoModeEnum,
        PortChannelDuplexEnum,
        VpcRoleEnum,
        MaintenanceModeEnum,
        ComponentTypeOverviewEnum,
        ComponentTypeSupportEnum,
        VpcPairViewEnum,
        VpcFieldNames,
    )
    from ansible_collections.cisco.nd.plugins.module_utils.manage.vpc_pair.base_paths import VpcPairBasePath

except ImportError as e:
    # Pydantic not available - components will not be exposed
    # This allows the package to be imported without pydantic for basic functionality
    _ = e
