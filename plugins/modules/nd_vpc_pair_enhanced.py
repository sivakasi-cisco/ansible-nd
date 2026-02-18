# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Sivakami S <sivakasi@cisco.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type
__copyright__ = "Copyright (c) 2026 Cisco and/or its affiliates."
__author__ = "Sivakami S"

DOCUMENTATION = """
---
module: nd_vpc_pair
short_description: Manage vPC pairs in Nexus devices.
version_added: "1.0.0"
description:
- Create, update, delete, override, and gather vPC pairs on Nexus devices.
- Uses NDNetworkResourceModule framework with custom action functions.
- Integrates RestSend for battle-tested HTTP handling with retry logic.
- Overcomes VPC pair API limitations via actions_overwrite_map.
options:
    state:
        choices:
        - merged
        - replaced
        - deleted
        - overridden
        - gathered
        default: merged
        description:
        - The state of the vPC pair configuration after module completion.
        type: str
    fabric_name:
        description:
        - Name of the fabric.
        required: true
        type: str
    deploy:
        description:
        - Deploy configuration changes after applying them.
        - Saves fabric configuration and triggers deployment.
        type: bool
        default: false
    dry_run:
        description:
        - Show what changes would be made without executing them.
        - Maps to Ansible check_mode internally.
        type: bool
        default: false
    config:
        description:
        - List of vPC pair configuration dictionaries.
        type: list
        elements: dict
        suboptions:
            peer1_switch_id:
                description:
                - Peer1 switch serial number for the vPC pair.
                required: true
                type: str
            peer2_switch_id:
                description:
                - Peer2 switch serial number for the vPC pair.
                required: true
                type: str
            use_virtual_peer_link:
                description:
                - Enable virtual peer link for the vPC pair.
                type: bool
                default: true
notes:
    - This module uses NDNetworkResourceModule framework for state management
    - RestSend provides protocol-based HTTP abstraction with automatic retry logic
    - Results are aggregated using the Results class for consistent output format
    - Check mode is fully supported via both framework and RestSend
"""

EXAMPLES = """
# Create a new vPC pair
- name: Create vPC pair
  cisco.nd.nd_vpc_pair:
    fabric_name: myFabric
    state: merged
    config:
      - peer1_switch_id: "FDO23040Q85"
        peer2_switch_id: "FDO23040Q86"
        use_virtual_peer_link: true

# Delete a vPC pair
- name: Delete vPC pair
  cisco.nd.nd_vpc_pair:
    fabric_name: myFabric
    state: deleted
    config:
      - peer1_switch_id: "FDO23040Q85"
        peer2_switch_id: "FDO23040Q86"

# Gather existing vPC pairs
- name: Gather all vPC pairs
  cisco.nd.nd_vpc_pair:
    fabric_name: myFabric
    state: gathered

# Create and deploy
- name: Create vPC pair and deploy
  cisco.nd.nd_vpc_pair:
    fabric_name: myFabric
    state: merged
    deploy: true
    config:
      - peer1_switch_id: "FDO23040Q85"
        peer2_switch_id: "FDO23040Q86"

# Dry run to see what would change
- name: Dry run vPC pair creation
  cisco.nd.nd_vpc_pair:
    fabric_name: myFabric
    state: merged
    dry_run: true
    config:
      - peer1_switch_id: "FDO23040Q85"
        peer2_switch_id: "FDO23040Q86"
"""

RETURN = """
changed:
    description: Whether the module made any changes
    type: bool
    returned: always
    sample: true
before:
    description: vPC pair state before changes
    type: list
    returned: always
    sample: [{"switchId": "FDO123", "peerSwitchId": "FDO456", "useVirtualPeerLink": false}]
after:
    description: vPC pair state after changes
    type: list
    returned: always
    sample: [{"switchId": "FDO123", "peerSwitchId": "FDO456", "useVirtualPeerLink": true}]
gathered:
    description: Current vPC pairs (gathered state only)
    type: dict
    returned: when state is gathered
    contains:
        vpc_pairs:
            description: List of configured VPC pairs
            type: list
        pending_create_vpc_pairs:
            description: VPC pairs ready to be created (switches are paired but VPC not configured)
            type: list
        pending_delete_vpc_pairs:
            description: VPC pairs in transitional delete state
            type: list
    sample:
        vpc_pairs: [{"switchId": "FDO123", "peerSwitchId": "FDO456"}]
        pending_create_vpc_pairs: []
        pending_delete_vpc_pairs: []
response:
    description: List of all API responses
    type: list
    returned: always
    sample: [{"RETURN_CODE": 200, "METHOD": "PUT", "MESSAGE": "Success"}]
result:
    description: List of all operation results
    type: list
    returned: always
    sample: [{"success": true, "changed": true}]
diff:
    description: List of all changes made, organized by operation
    type: list
    returned: always
    contains:
        operation:
            description: Type of operation (POST/PUT/DELETE)
            type: str
        vpc_pair_key:
            description: Identifier for the VPC pair (switchId-peerSwitchId)
            type: str
        path:
            description: API endpoint path used
            type: str
        payload:
            description: Request payload sent to API
            type: dict
    sample: [{"operation": "PUT", "vpc_pair_key": "FDO123-FDO456", "path": "/api/v1/...", "payload": {}}]
metadata:
    description: Operation metadata with sequence and identifiers
    type: dict
    returned: when operations are performed
    contains:
        vpc_pair_key:
            description: VPC pair identifier
            type: str
        operation:
            description: Operation type (create/update/delete)
            type: str
        sequence_number:
            description: Operation sequence in batch
            type: int
    sample: {"vpc_pair_key": "FDO123-FDO456", "operation": "create", "sequence_number": 1}
warnings:
    description: List of warning messages from validation or operations
    type: list
    returned: when warnings occur
    sample: ["VPC pair has 2 vPC interfaces - deletion may require manual cleanup"]
failed:
    description: Whether any operation failed
    type: bool
    returned: when operations fail
    sample: false
ip_to_sn_mapping:
    description: Mapping of switch IP addresses to serial numbers
    type: dict
    returned: when available from fabric inventory
    sample: {"10.1.1.1": "FDO123", "10.1.1.2": "FDO456"}
deployment:
    description: Deployment operation results (when deploy=true)
    type: dict
    returned: when deploy parameter is true
    contains:
        deployment_needed:
            description: Whether deployment was needed based on changes
            type: bool
        changed:
            description: Whether deployment made changes
            type: bool
        response:
            description: List of deployment API responses (save and deploy)
            type: list
    sample: {"deployment_needed": true, "changed": true, "response": [...]}
deployment_needed:
    description: Flag indicating if deployment was needed
    type: bool
    returned: when deploy=true
    sample: true
pending_create_pairs_not_in_delete:
    description: VPC pairs in pending create state not included in delete wants (deleted state only)
    type: list
    returned: when state is deleted and pending create pairs exist
    sample: [{"switchId": "FDO789", "peerSwitchId": "FDO012"}]
pending_delete_pairs_not_in_delete:
    description: VPC pairs in pending delete state not included in delete wants (deleted state only)
    type: list
    returned: when state is deleted and pending delete pairs exist
    sample: []
"""

import json
import logging
import sys
import traceback
from typing import Any, Dict, List, Optional, Union

from ansible.module_utils.basic import AnsibleModule, missing_required_lib

# Framework imports
from ansible_collections.cisco.nd.plugins.module_utils.nd_network_resources import (
    NDNetworkResourceModule,
)
from ansible_collections.cisco.nd.plugins.module_utils.models.base import NDBaseModel
from ansible_collections.cisco.nd.plugins.module_utils.enums import HttpVerbEnum

# RestSend imports 
from ansible_collections.cisco.nd.plugins.module_utils.nd_v2 import (
    NDModule as NDModuleV2,
    NDModuleError,
)
from ansible_collections.cisco.nd.plugins.module_utils.results import Results

# Pydantic imports
from pydantic import Field, field_validator, model_validator

# VPC Pair schema imports (for vpc_pair_details support)
from ansible_collections.cisco.nd.plugins.module_utils.manage.vpc_pair.model_playbook_vpc_pair import (
    VpcPairDetailsDefault,
    VpcPairDetailsCustom,
)

# DeepDiff for intelligent change detection
try:
    from deepdiff import DeepDiff
    HAS_DEEPDIFF = True
    DEEPDIFF_IMPORT_ERROR = None
except ImportError:
    HAS_DEEPDIFF = False
    DEEPDIFF_IMPORT_ERROR = traceback.format_exc()


# ===== Constants =====


class VpcPairConstants:
    """
    Constants for VPC pair operations.

    Centralized field names, action types, and status fields to:
    - Eliminate magic strings
    - Enable IDE autocomplete
    - Prevent typos
    - Easy refactoring
    """

    # VPC Action Discriminators
    VPC_ACTION = "vpcAction"
    VPC_ACTION_PAIR = "pair"
    VPC_ACTION_UNPAIR = "unpair"

    # Primary Identifier Fields (API format)
    FIELD_SWITCH_ID = "switchId"
    FIELD_PEER_SWITCH_ID = "peerSwitchId"
    FIELD_USE_VIRTUAL_PEER_LINK = "useVirtualPeerLink"

    # Ansible Playbook Fields (user input)
    ANSIBLE_PEER1_SWITCH_ID = "peer1SwitchId"
    ANSIBLE_PEER2_SWITCH_ID = "peer2SwitchId"

    # Configuration Fields
    FIELD_VPC_PAIR_DETAILS = "vpcPairDetails"
    FIELD_DOMAIN_ID = "domainId"
    FIELD_SWITCH_NAME = "switchName"
    FIELD_PEER_SWITCH_NAME = "peerSwitchName"

    # Status Fields
    STATUS_VPC_CONFIGURED = "vpcConfigured"
    STATUS_CONFIG_SYNC = "configSyncStatus"
    STATUS_CURRENT_PEER = "currentPeer"
    STATUS_IS_CURRENT_PEER = "isCurrentPeer"
    STATUS_IS_CONSISTENT = "isConsistent"
    STATUS_IS_DISCOVERED = "isDiscovered"

    # Response Keys
    KEY_VPC_PAIRS = "vpcPairs"
    KEY_SWITCHES = "switches"
    KEY_DATA = "data"

    # Network Fields
    FIELD_FABRIC_MGMT_IP = "fabricManagementIp"
    FIELD_SERIAL_NUMBER = "serialNumber"
    FIELD_IP_ADDRESS = "ipAddress"

    # Validation Fields (for pre-deletion checks)
    KEY_OVERLAY = "overlay"
    KEY_INVENTORY = "inventory"
    FIELD_NETWORK_COUNT = "networkCount"
    FIELD_VRF_COUNT = "vrfCount"
    FIELD_VPC_INTERFACE_COUNT = "vpcInterfaceCount"


class VpcPairEndpoints:
    """
    Centralized API endpoint path management for VPC pair operations.

    All API endpoint paths are defined here to:
    - Eliminate scattered path definitions
    - Make API evolution easier
    - Enable easy endpoint discovery
    - Support multiple API versions

    Usage:
        # Get a path with parameters
        path = VpcPairEndpoints.vpc_pair_put(fabric_name="myFabric", switch_id="FDO123")
        # Returns: "/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/vpcpair/fabrics/myFabric/switches/FDO123"
    """

    # Base paths
    NDFC_BASE = "/appcenter/cisco/ndfc/api/v1/lan-fabric/rest"
    MANAGE_BASE = "/api/v1/manage"

    # Path templates for VPC pair operations (NDFC API)
    VPC_PAIR_BASE = f"{NDFC_BASE}/vpcpair/fabrics/{{fabric_name}}"
    VPC_PAIR_SWITCH = f"{NDFC_BASE}/vpcpair/fabrics/{{fabric_name}}/switches/{{switch_id}}"

    # Path templates for fabric operations (Manage API - for config save/deploy actions)
    FABRIC_CONFIG_SAVE = f"{MANAGE_BASE}/fabrics/{{fabric_name}}/actions/configSave"
    FABRIC_CONFIG_DEPLOY = f"{MANAGE_BASE}/fabrics/{{fabric_name}}/actions/deploy"

    # Path templates for switch/inventory operations (Manage API)
    FABRIC_SWITCHES = f"{MANAGE_BASE}/fabrics/{{fabric_name}}/switches"
    SWITCH_VPC_PAIR = f"{MANAGE_BASE}/fabrics/{{fabric_name}}/switches/{{switch_id}}/vpcPair"
    SWITCH_VPC_RECOMMENDATIONS = f"{MANAGE_BASE}/fabrics/{{fabric_name}}/switches/{{switch_id}}/vpcPairRecommendations"
    SWITCH_VPC_OVERVIEW = f"{MANAGE_BASE}/fabrics/{{fabric_name}}/switches/{{switch_id}}/vpcPairOverview"

    @staticmethod
    def vpc_pair_base(fabric_name: str) -> str:
        """
        Get base path for VPC pair operations.

        Args:
            fabric_name: Fabric name

        Returns:
            Base VPC pair path

        Example:
            >>> VpcPairEndpoints.vpc_pair_base("myFabric")
            '/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/vpcpair/fabrics/myFabric'
        """
        return VpcPairEndpoints.VPC_PAIR_BASE.format(fabric_name=fabric_name)

    @staticmethod
    def vpc_pair_put(fabric_name: str, switch_id: str) -> str:
        """
        Get path for VPC pair PUT operations (create/update/delete).

        Args:
            fabric_name: Fabric name
            switch_id: Switch serial number

        Returns:
            VPC pair PUT path

        Example:
            >>> VpcPairEndpoints.vpc_pair_put("myFabric", "FDO123")
            '/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/vpcpair/fabrics/myFabric/switches/FDO123'
        """
        return VpcPairEndpoints.VPC_PAIR_SWITCH.format(
            fabric_name=fabric_name,
            switch_id=switch_id
        )

    @staticmethod
    def fabric_switches(fabric_name: str) -> str:
        """
        Get path for querying fabric switch inventory.

        Args:
            fabric_name: Fabric name

        Returns:
            Fabric switches path

        Example:
            >>> VpcPairEndpoints.fabric_switches("myFabric")
            '/api/v1/manage/fabrics/myFabric/switches'
        """
        return VpcPairEndpoints.FABRIC_SWITCHES.format(fabric_name=fabric_name)

    @staticmethod
    def switch_vpc_pair(fabric_name: str, switch_id: str) -> str:
        """
        Get path for querying specific switch VPC pair.

        Args:
            fabric_name: Fabric name
            switch_id: Switch serial number

        Returns:
            Switch VPC pair path

        Example:
            >>> VpcPairEndpoints.switch_vpc_pair("myFabric", "FDO123")
            '/api/v1/manage/fabrics/myFabric/switches/FDO123/vpcPair'
        """
        return VpcPairEndpoints.SWITCH_VPC_PAIR.format(
            fabric_name=fabric_name,
            switch_id=switch_id
        )

    @staticmethod
    def switch_vpc_recommendations(fabric_name: str, switch_id: str) -> str:
        """
        Get path for querying VPC pair recommendations for a switch.

        Args:
            fabric_name: Fabric name
            switch_id: Switch serial number

        Returns:
            VPC recommendations path

        Example:
            >>> VpcPairEndpoints.switch_vpc_recommendations("myFabric", "FDO123")
            '/api/v1/manage/fabrics/myFabric/switches/FDO123/vpcPairRecommendations'
        """
        return VpcPairEndpoints.SWITCH_VPC_RECOMMENDATIONS.format(
            fabric_name=fabric_name,
            switch_id=switch_id
        )

    @staticmethod
    def switch_vpc_overview(fabric_name: str, switch_id: str, component_type: str = "full") -> str:
        """
        Get path for querying VPC pair overview (for pre-deletion validation).

        Args:
            fabric_name: Fabric name
            switch_id: Switch serial number
            component_type: Component type ("full" or "minimal"), default "full"

        Returns:
            VPC overview path with query parameters

        Example:
            >>> VpcPairEndpoints.switch_vpc_overview("myFabric", "FDO123")
            '/api/v1/manage/fabrics/myFabric/switches/FDO123/vpcPairOverview?componentType=full'
        """
        base_path = VpcPairEndpoints.SWITCH_VPC_OVERVIEW.format(
            fabric_name=fabric_name,
            switch_id=switch_id
        )
        return f"{base_path}?componentType={component_type}"

    @staticmethod
    def fabric_config_save(fabric_name: str) -> str:
        """
        Get path for saving fabric configuration.

        Args:
            fabric_name: Fabric name

        Returns:
            Fabric config save path

        Example:
            >>> VpcPairEndpoints.fabric_config_save("myFabric")
            '/api/v1/manage/fabrics/myFabric/actions/configSave'
        """
        return VpcPairEndpoints.FABRIC_CONFIG_SAVE.format(fabric_name=fabric_name)

    @staticmethod
    def fabric_config_deploy(fabric_name: str, force_show_run: bool = True) -> str:
        """
        Get path for deploying fabric configuration.

        Args:
            fabric_name: Fabric name
            force_show_run: Include forceShowRun query parameter, default True

        Returns:
            Fabric config deploy path with query parameters

        Example:
            >>> VpcPairEndpoints.fabric_config_deploy("myFabric")
            '/api/v1/manage/fabrics/myFabric/actions/deploy?forceShowRun=true'
        """
        base_path = VpcPairEndpoints.FABRIC_CONFIG_DEPLOY.format(fabric_name=fabric_name)
        if force_show_run:
            return f"{base_path}?forceShowRun=true"
        return base_path


# ===== VPC Pair Model =====


class VpcPairModel(NDBaseModel):
    """
    Pydantic model for VPC pair configuration.

    Uses composite identifier: (switch_id, peer_switch_id)
    """

    # Identifier configuration
    identifiers = ["switch_id", "peer_switch_id"]
    identifier_strategy = "composite"

    # Fields (Ansible names -> API aliases)
    switch_id: str = Field(
        alias=VpcPairConstants.FIELD_SWITCH_ID,
        description="Peer-1 switch serial number",
        min_length=3,
        max_length=64
    )
    peer_switch_id: str = Field(
        alias=VpcPairConstants.FIELD_PEER_SWITCH_ID,
        description="Peer-2 switch serial number",
        min_length=3,
        max_length=64
    )
    use_virtual_peer_link: bool = Field(
        default=True,
        alias=VpcPairConstants.FIELD_USE_VIRTUAL_PEER_LINK,
        description="Virtual peer link enabled"
    )
    vpc_pair_details: Optional[Union[VpcPairDetailsDefault, VpcPairDetailsCustom]] = Field(
        default=None,
        discriminator="type",
        alias=VpcPairConstants.FIELD_VPC_PAIR_DETAILS,
        description="VPC pair configuration details (default or custom template)"
    )

    @field_validator("switch_id", "peer_switch_id")
    @classmethod
    def validate_switch_id_format(cls, v: str) -> str:
        """
        Validate switch ID is not empty or whitespace.

        Args:
            v: Switch ID value

        Returns:
            Stripped switch ID

        Raises:
            ValueError: If switch ID is empty or whitespace
        """
        if not v or not v.strip():
            raise ValueError("Switch ID cannot be empty or whitespace")
        return v.strip()

    @model_validator(mode="after")
    def validate_different_switches(self) -> "VpcPairModel":
        """
        Ensure switch_id and peer_switch_id are different.

        Returns:
            Validated model instance

        Raises:
            ValueError: If switch_id equals peer_switch_id
        """
        if self.switch_id == self.peer_switch_id:
            raise ValueError(
                f"switch_id and peer_switch_id must be different: {self.switch_id}"
            )
        return self

    def to_payload(self) -> Dict[str, Any]:
        """
        Convert to API payload format.

        Note: vpcAction is added by custom functions, not here.
        """
        return self.model_dump(by_alias=True, exclude_none=True)

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> "VpcPairModel":
        """
        Parse VPC pair from API response.

        Handles API field name variations.
        """
        data = {
            VpcPairConstants.FIELD_SWITCH_ID: response.get(VpcPairConstants.FIELD_SWITCH_ID),
            VpcPairConstants.FIELD_PEER_SWITCH_ID: response.get(VpcPairConstants.FIELD_PEER_SWITCH_ID),
            VpcPairConstants.FIELD_USE_VIRTUAL_PEER_LINK: response.get(
                VpcPairConstants.FIELD_USE_VIRTUAL_PEER_LINK, True
            ),
        }
        return cls.model_validate(data)


# ===== Helper Functions =====


def _is_update_needed(want: Dict[str, Any], have: Dict[str, Any]) -> bool:
    """
    Determine if an update is needed by comparing want and have using DeepDiff.

    Uses DeepDiff for intelligent comparison that handles:
    - Field additions
    - Value changes
    - Nested structure changes
    - Ignores field order

    Falls back to simple comparison if DeepDiff is unavailable.

    Args:
        want: Desired VPC pair configuration (dict)
        have: Current VPC pair configuration (dict)

    Returns:
        bool: True if update is needed, False if already in desired state

    Example:
        >>> want = {"switchId": "FDO123", "useVirtualPeerLink": True}
        >>> have = {"switchId": "FDO123", "useVirtualPeerLink": False}
        >>> _is_update_needed(want, have)
        True
    """
    if not HAS_DEEPDIFF:
        # Fallback to simple comparison
        return want != have

    try:
        # Use DeepDiff for intelligent comparison
        diff = DeepDiff(have, want, ignore_order=True)
        return bool(diff)
    except Exception:
        # Fallback to simple comparison if DeepDiff fails
        return want != have


def _get_template_config(vpc_pair_model) -> Optional[Dict[str, Any]]:
    """
    Extract template configuration from VPC pair model if present.

    Supports both default and custom template types:
    - default: Standard parameters (domainId, keepAliveVrf, etc.)
    - custom: User-defined template with custom fields

    Args:
        vpc_pair_model: VpcPairModel instance

    Returns:
        dict: Template configuration or None if not provided

    Example:
        # For default template:
        config = _get_template_config(model)
        # Returns: {"type": "default", "domainId": 100, ...}

        # For custom template:
        config = _get_template_config(model)
        # Returns: {"type": "custom", "templateName": "my_template", ...}
    """
    # Check if model has vpc_pair_details
    if not hasattr(vpc_pair_model, "vpc_pair_details"):
        return None

    vpc_pair_details = vpc_pair_model.vpc_pair_details
    if not vpc_pair_details:
        return None

    # Return the validated Pydantic model as dict
    return vpc_pair_details.model_dump(by_alias=True, exclude_none=True)


def _build_vpc_pair_payload(vpc_pair_model) -> Dict[str, Any]:
    """
    Build the 4.2 API payload for pairing a VPC.

    Constructs payload according to OpenAPI spec with vpcAction
    discriminator and optional template details.

    Args:
        vpc_pair_model: VpcPairModel instance with configuration

    Returns:
        dict: Complete payload for PUT request in 4.2 format

    Example:
        payload = _build_vpc_pair_payload(vpc_pair_model)
        # Returns:
        # {
        #     "vpcAction": "pair",
        #     "switchId": "FDO123",
        #     "peerSwitchId": "FDO456",
        #     "useVirtualPeerLink": True,
        #     "vpcPairDetails": {...}  # Optional
        # }
    """
    # Base payload with vpcAction discriminator
    payload = {
        VpcPairConstants.VPC_ACTION: VpcPairConstants.VPC_ACTION_PAIR,
        VpcPairConstants.FIELD_SWITCH_ID: vpc_pair_model.switch_id,
        VpcPairConstants.FIELD_PEER_SWITCH_ID: vpc_pair_model.peer_switch_id,
        VpcPairConstants.FIELD_USE_VIRTUAL_PEER_LINK: vpc_pair_model.use_virtual_peer_link,
    }

    # Add template configuration if provided
    template_config = _get_template_config(vpc_pair_model)
    if template_config:
        payload[VpcPairConstants.FIELD_VPC_PAIR_DETAILS] = template_config

    return payload


def _get_recommendation_details(nd_v2, fabric_name: str, switch_id: str) -> Optional[Dict]:
    """
    Get VPC pair recommendation details from ND for a specific switch.
    
    Returns peer switch info and useVirtualPeerLink status.
    
    Args:
        nd_v2: NDModuleV2 instance for RestSend
        fabric_name: Fabric name
        switch_id: Switch serial number
        
    Returns:
        Dict with peer info or None if not available
    """
    try:
        path = VpcPairEndpoints.switch_vpc_recommendations(fabric_name, switch_id)
        vpc_recommendations = nd_v2.request(path, HttpVerbEnum.GET, ignore_not_found_error=True)
        
        if vpc_recommendations is None or vpc_recommendations == {}:
            return None
            
        # Look for current peer in recommendations list
        if isinstance(vpc_recommendations, list):
            for sw in vpc_recommendations:
                if isinstance(sw, dict) and (
                    sw.get(VpcPairConstants.STATUS_CURRENT_PEER) or
                    sw.get(VpcPairConstants.STATUS_IS_CURRENT_PEER)
                ):
                    return sw
                    
        return None
    except Exception:
        return None


def _validate_fabric_switches(nd_v2, fabric_name: str) -> Dict[str, Dict]:
    """
    Query and validate fabric switch inventory.
    
    Args:
        nd_v2: NDModuleV2 instance for RestSend
        fabric_name: Fabric name
        
    Returns:
        Dict mapping switch serial number to switch info
        
    Raises:
        NDModuleError: If fabric switch query fails
    """
    switches_path = VpcPairEndpoints.fabric_switches(fabric_name)
    switches_response = nd_v2.request(switches_path, HttpVerbEnum.GET)
    
    if not switches_response:
        return {}
        
    switches = switches_response.get(VpcPairConstants.KEY_SWITCHES, [])
    return {sw.get(VpcPairConstants.FIELD_SERIAL_NUMBER): sw for sw in switches if VpcPairConstants.FIELD_SERIAL_NUMBER in sw}


def _validate_switch_conflicts(want_configs: List[Dict], have_vpc_pairs: List[Dict], module) -> None:
    """
    Validate that switches in want configs aren't already in different VPC pairs.
    
    Args:
        want_configs: List of desired VPC pair configs
        have_vpc_pairs: List of existing VPC pairs
        module: AnsibleModule instance for fail_json
        
    Raises:
        AnsibleModule.fail_json: If switch conflicts detected
    """
    conflicts = []
    
    for want in want_configs:
        want_switches = {want.get(VpcPairConstants.FIELD_SWITCH_ID), want.get(VpcPairConstants.FIELD_PEER_SWITCH_ID)}
        want_switches.discard(None)
        
        for have in have_vpc_pairs:
            have_switches = {have.get(VpcPairConstants.FIELD_SWITCH_ID), have.get(VpcPairConstants.FIELD_PEER_SWITCH_ID)}
            have_switches.discard(None)
            
            # Same VPC pair is OK
            if want_switches == have_switches:
                continue
                
            # Check for switch overlap with different pairs
            switch_overlap = want_switches & have_switches
            if switch_overlap:
                # Filter out None values and ensure strings for joining
                overlap_list = [str(s) for s in switch_overlap if s is not None]
                want_key = f"{want.get(VpcPairConstants.FIELD_SWITCH_ID)}-{want.get(VpcPairConstants.FIELD_PEER_SWITCH_ID)}"
                have_key = f"{have.get(VpcPairConstants.FIELD_SWITCH_ID)}-{have.get(VpcPairConstants.FIELD_PEER_SWITCH_ID)}"
                conflicts.append(
                    f"Switch(es) {', '.join(overlap_list)} in wanted VPC pair {want_key} "
                    f"are already part of existing VPC pair {have_key}"
                )
    
    if conflicts:
        module.fail_json(
            msg="Switch conflicts detected. A switch can only be part of one VPC pair at a time.",
            conflicts=conflicts
        )


def _validate_vpc_pair_deletion(nd_v2, fabric_name: str, switch_id: str, vpc_pair_key: str, module) -> None:
    """
    Validate VPC pair can be safely deleted by checking for dependencies.

    This function prevents data loss by ensuring the VPC pair has no active:
    1. Networks (networkCount must be 0 for all statuses)
    2. VRFs (vrfCount must be 0 for all statuses)
    3. Warns if vPC interfaces exist (vpcInterfaceCount > 0)

    Args:
        nd_v2: NDModuleV2 instance for RestSend
        fabric_name: Fabric name
        switch_id: Switch serial number
        vpc_pair_key: VPC pair identifier (e.g., "FDO123-FDO456") for error messages
        module: AnsibleModule instance for fail_json/warn

    Raises:
        AnsibleModule.fail_json: If VPC pair has active networks or VRFs

    Example:
        _validate_vpc_pair_deletion(nd_v2, "myFabric", "FDO123", "FDO123-FDO456", module)
    """
    try:
        # Query overview endpoint with full component data
        overview_path = VpcPairEndpoints.switch_vpc_overview(fabric_name, switch_id, component_type="full")

        response = nd_v2.request(overview_path, HttpVerbEnum.GET, ignore_not_found_error=True)

        # If no response, VPC pair doesn't exist - deletion not needed
        if not response:
            module.warn(
                f"VPC pair {vpc_pair_key} not found in overview query. "
                f"It may not exist or may have already been deleted."
            )
            return

        # Validate response structure
        if not isinstance(response, dict):
            module.fail_json(
                msg=f"Expected dict response from vPC pair overview for {vpc_pair_key}, got {type(response).__name__}",
                response=response
            )

        # Validate overlay data exists
        overlay = response.get(VpcPairConstants.KEY_OVERLAY)
        if not overlay:
            module.fail_json(
                msg=(
                    f"vPC pair {vpc_pair_key} might not exist or overlay data unavailable. "
                    f"Cannot safely validate deletion."
                ),
                vpc_pair_key=vpc_pair_key,
                response=response
            )
            return  # Unreachable, but satisfies type checker

        # Check 1: Validate no networks are attached
        network_count = overlay.get(VpcPairConstants.FIELD_NETWORK_COUNT, {})
        if isinstance(network_count, dict):
            for status, count in network_count.items():
                try:
                    count_int = int(count)
                    if count_int != 0:
                        module.fail_json(
                            msg=(
                                f"Cannot delete vPC pair {vpc_pair_key}. "
                                f"{count_int} network(s) with status '{status}' still exist. "
                                f"Remove all networks from this vPC pair before deleting it."
                            ),
                            vpc_pair_key=vpc_pair_key,
                            network_count=network_count,
                            blocking_status=status,
                            blocking_count=count_int
                        )
                except (ValueError, TypeError) as e:
                    # Best effort - log warning and continue
                    module.warn(f"Error parsing network count for status '{status}': {e}")
        elif network_count:
            # Non-dict format - log warning
            module.warn(
                f"networkCount is not a dict for {vpc_pair_key}: {type(network_count).__name__}. "
                f"Skipping network validation."
            )

        # Check 2: Validate no VRFs are attached
        vrf_count = overlay.get(VpcPairConstants.FIELD_VRF_COUNT, {})
        if isinstance(vrf_count, dict):
            for status, count in vrf_count.items():
                try:
                    count_int = int(count)
                    if count_int != 0:
                        module.fail_json(
                            msg=(
                                f"Cannot delete vPC pair {vpc_pair_key}. "
                                f"{count_int} VRF(s) with status '{status}' still exist. "
                                f"Remove all VRFs from this vPC pair before deleting it."
                            ),
                            vpc_pair_key=vpc_pair_key,
                            vrf_count=vrf_count,
                            blocking_status=status,
                            blocking_count=count_int
                        )
                except (ValueError, TypeError) as e:
                    # Best effort - log warning and continue
                    module.warn(f"Error parsing VRF count for status '{status}': {e}")
        elif vrf_count:
            # Non-dict format - log warning
            module.warn(
                f"vrfCount is not a dict for {vpc_pair_key}: {type(vrf_count).__name__}. "
                f"Skipping VRF validation."
            )

        # Check 3: Warn if vPC interfaces exist (non-blocking)
        inventory = response.get(VpcPairConstants.KEY_INVENTORY, {})
        if inventory and isinstance(inventory, dict):
            vpc_interface_count = inventory.get(VpcPairConstants.FIELD_VPC_INTERFACE_COUNT)
            if vpc_interface_count:
                try:
                    count_int = int(vpc_interface_count)
                    if count_int > 0:
                        module.warn(
                            f"vPC pair {vpc_pair_key} has {count_int} vPC interface(s). "
                            f"Deletion may fail or require manual cleanup of interfaces. "
                            f"Consider removing vPC interfaces before deleting the vPC pair."
                        )
                except (ValueError, TypeError) as e:
                    # Best effort - just log debug message
                    pass
        elif not inventory:
            # No inventory data - warn user
            module.warn(
                f"Inventory data not available in overview response for {vpc_pair_key}. "
                f"Proceeding with deletion, but it may fail if vPC interfaces exist."
            )

    except NDModuleError as error:
        # Best effort validation - if overview query fails, log warning and proceed
        # The API will still reject deletion if dependencies exist
        module.warn(
            f"Could not validate vPC pair {vpc_pair_key} for deletion: {error.msg}. "
            f"Proceeding with deletion attempt. API will reject if dependencies exist."
        )

    except Exception as e:
        # Best effort validation - log warning and continue
        module.warn(
            f"Unexpected error validating VPC pair {vpc_pair_key} for deletion: {str(e)}. "
            f"Proceeding with deletion attempt."
        )


# ===== Custom Action Functions (using RestSend + actions_overwrite_map) =====


def custom_vpc_query_all(nrm) -> List[Dict]:
    """
    Custom query function for VPC pairs using RestSend with full state tracking.

    - Validates fabric and queries switch inventory (UpdateInventory)
    - Tracks 3-state: have, pending_create, pending_delete (GetHave)
    - Queries recommendation API for virtual peer link details
    - Falls back to direct VPC query if recommendation fails
    - Builds IP-to-SN mapping from switch inventory
    - Stores fabric switches for validation

    Args:
        nrm: NDNetworkResourceModule instance

    Returns:
        List of VPC pair dictionaries from API (have state)

    Raises:
        ValueError: If fabric_name is not configured
        NDModuleError: If critical queries fail
    """
    fabric_name = nrm.module.params.get("fabric_name")

    # Fabric validation (from UpdateInventory.__init__)
    if not fabric_name or not isinstance(fabric_name, str) or not fabric_name.strip():
        raise ValueError(f"fabric_name must be a non-empty string. Got: {fabric_name!r}")

    # Initialize RestSend via NDModuleV2
    nd_v2 = NDModuleV2(nrm.module)

    try:
        # Step 1: Query and validate fabric switches (UpdateInventory.refresh())
        fabric_switches = _validate_fabric_switches(nd_v2, fabric_name)
        
        if not fabric_switches:
            nrm.module.warn(f"No switches found in fabric {fabric_name}")
            nrm.module.params["_fabric_switches"] = {}
            nrm.module.params["_have"] = []
            nrm.module.params["_pending_create"] = []
            nrm.module.params["_pending_delete"] = []
            return []
        
        # Store for validation in create/update/delete actions
        nrm.module.params["_fabric_switches"] = fabric_switches
        
        # Build IP-to-SN mapping
        ip_to_sn = {
            sw.get(VpcPairConstants.FIELD_FABRIC_MGMT_IP): sw.get(VpcPairConstants.FIELD_SERIAL_NUMBER)
            for sw in fabric_switches.values()
            if VpcPairConstants.FIELD_FABRIC_MGMT_IP in sw
        }
        nrm.module.params["_ip_to_sn_mapping"] = ip_to_sn
        
        # Step 2: Track 3-state VPC pairs (GetHave.refresh())
        have = []
        pending_create = []
        pending_delete = []
        processed_switches = set()
        
        for switch_id, switch in fabric_switches.items():
            if switch_id in processed_switches:
                continue
                
            vpc_configured = switch.get(VpcPairConstants.STATUS_VPC_CONFIGURED, False)
            vpc_data = switch.get("vpcData", {})
            
            if vpc_configured and vpc_data:
                peer_switch_id = vpc_data.get("peerSwitchId")
                processed_switches.add(switch_id)
                processed_switches.add(peer_switch_id)
                
                # Try recommendation API for useVirtualPeerLink status
                recommendation = _get_recommendation_details(nd_v2, fabric_name, switch_id)
                
                if recommendation:
                    # VPC pair is fully configured
                    use_vpl = recommendation.get("useVirtualPeerlink", recommendation.get("useVirtualPeerLink", False))
                    have.append({
                        VpcPairConstants.FIELD_SWITCH_ID: switch_id,
                        VpcPairConstants.FIELD_PEER_SWITCH_ID: peer_switch_id,
                        VpcPairConstants.FIELD_USE_VIRTUAL_PEER_LINK: use_vpl,
                    })
                else:
                    # Recommendation failed - query VPC pair directly
                    vpc_pair_path = VpcPairEndpoints.switch_vpc_pair(fabric_name, switch_id)
                    direct_vpc = nd_v2.request(vpc_pair_path, HttpVerbEnum.GET, ignore_not_found_error=True)
                    
                    if direct_vpc:
                        use_vpl = direct_vpc.get(VpcPairConstants.FIELD_USE_VIRTUAL_PEER_LINK, False)
                        have.append({
                            VpcPairConstants.FIELD_SWITCH_ID: switch_id,
                            VpcPairConstants.FIELD_PEER_SWITCH_ID: peer_switch_id,
                            VpcPairConstants.FIELD_USE_VIRTUAL_PEER_LINK: use_vpl,
                        })
                    else:
                        # VPC configured but query failed - mark as pending delete
                        pending_delete.append({
                            VpcPairConstants.FIELD_SWITCH_ID: switch_id,
                            VpcPairConstants.FIELD_PEER_SWITCH_ID: peer_switch_id,
                            VpcPairConstants.FIELD_USE_VIRTUAL_PEER_LINK: False,
                        })
            else:
                # Check if switch has recommendation (ready to pair)
                recommendation = _get_recommendation_details(nd_v2, fabric_name, switch_id)
                
                if recommendation:
                    peer_switch_id = recommendation.get("serialNumber")
                    if peer_switch_id:
                        processed_switches.add(switch_id)
                        processed_switches.add(peer_switch_id)
                        
                        use_vpl = recommendation.get("useVirtualPeerlink", recommendation.get("useVirtualPeerLink", False))
                        pending_create.append({
                            VpcPairConstants.FIELD_SWITCH_ID: switch_id,
                            VpcPairConstants.FIELD_PEER_SWITCH_ID: peer_switch_id,
                            VpcPairConstants.FIELD_USE_VIRTUAL_PEER_LINK: use_vpl,
                        })
        
        # Step 3: Store all states for use in create/update/delete
        nrm.module.params["_have"] = have
        nrm.module.params["_pending_create"] = pending_create
        nrm.module.params["_pending_delete"] = pending_delete
        
        return have

    except NDModuleError as error:
        nrm.module.fail_json(
            msg=f"Failed to query VPC pairs: {error.msg}",
            fabric=fabric_name,
            status=error.status,
            **error.to_dict()
        )
        return []  # Unreachable, but satisfies type checker
    except Exception as e:
        nrm.module.fail_json(
            msg=f"Failed to query VPC pairs: {str(e)}",
            fabric=fabric_name,
            exception_type=type(e).__name__
        )
        return []  # Unreachable, but satisfies type checker


def custom_vpc_create(nrm) -> Optional[Dict[str, Any]]:
    """
    Custom create function for VPC pairs using RestSend with PUT + discriminator.
    - Validates switches exist in fabric (Common.validate_switches_exist)
    - Checks for switch conflicts (Common.validate_no_switch_conflicts)
    - Uses PUT instead of POST (non-RESTful API)
    - Adds vpcAction: "pair" discriminator
    - Proper error handling with NDModuleError
    - Results aggregation

    Args:
        nrm: NDNetworkResourceModule instance

    Returns:
        API response dictionary or None

    Raises:
        ValueError: If fabric_name or switch_id is not provided
        AnsibleModule.fail_json: If validation fails
    """
    if nrm.module.check_mode:
        return nrm.proposed_config

    fabric_name = nrm.module.params.get("fabric_name")
    switch_id = nrm.proposed_config.get(VpcPairConstants.FIELD_SWITCH_ID)
    peer_switch_id = nrm.proposed_config.get(VpcPairConstants.FIELD_PEER_SWITCH_ID)

    # Path validation
    if not fabric_name:
        raise ValueError("fabric_name is required but was not provided")
    if not switch_id:
        raise ValueError("switch_id is required but was not provided")
    if not peer_switch_id:
        raise ValueError("peer_switch_id is required but was not provided")

    # Validation Step 1: Check switches exist in fabric (from Common.validate_switches_exist)
    fabric_switches = nrm.module.params.get("_fabric_switches", {})
    if fabric_switches:
        missing_switches = []
        if switch_id not in fabric_switches:
            missing_switches.append(switch_id)
        if peer_switch_id not in fabric_switches:
            missing_switches.append(peer_switch_id)

        if missing_switches:
            valid_switches = sorted(fabric_switches.keys())
            error_msg = (
                f"Switch validation failed: The following switch(es) do not exist in fabric '{fabric_name}':\n"
                f"  Missing switches: {', '.join(missing_switches)}\n"
                f"  Affected vPC pair: {nrm.current_identifier}\n\n"
                f"Please ensure:\n"
                f"  1. Switch serial numbers are correct (not IP addresses)\n"
                f"  2. Switches are discovered and present in the fabric\n"
                f"  3. You have the correct fabric name specified\n\n"
            )

            # Include limited valid switches list for reference
            if len(valid_switches) <= 10:
                error_msg += f"Valid switches in fabric: {', '.join(valid_switches)}"
            else:
                error_msg += f"Valid switches in fabric (first 10): {', '.join(valid_switches[:10])} ... and {len(valid_switches) - 10} more"

            nrm.module.fail_json(
                msg=error_msg,
                missing_switches=missing_switches,
                vpc_pair_key=nrm.current_identifier,
                total_valid_switches=len(valid_switches)
            )
    
    # Validation Step 2: Check for switch conflicts (from Common.validate_no_switch_conflicts)
    have_vpc_pairs = nrm.module.params.get("_have", [])
    if have_vpc_pairs:
        _validate_switch_conflicts([nrm.proposed_config], have_vpc_pairs, nrm.module)

    # Initialize RestSend via NDModuleV2
    nd_v2 = NDModuleV2(nrm.module)

    # Build path with switch ID
    path = VpcPairEndpoints.vpc_pair_put(fabric_name, switch_id)

    # Build payload with discriminator using helper (supports vpc_pair_details)
    payload = _build_vpc_pair_payload(nrm.proposed_config)

    # Log the operation
    nrm.format_log(
        identifier=nrm.current_identifier,
        status="created",
        after_data=payload,
        sent_payload_data=payload
    )

    try:
        # Use PUT (not POST!) for create via RestSend
        response = nd_v2.request(path, HttpVerbEnum.PUT, payload)
        return response

    except NDModuleError as error:
        nrm.module.fail_json(
            msg=f"Failed to create VPC pair {nrm.current_identifier}: {error.msg}",
            fabric=fabric_name,
            switch_id=switch_id,
            peer_switch_id=peer_switch_id,
            path=path,
            status=error.status,
            **error.to_dict()
        )
    except Exception as e:
        nrm.module.fail_json(
            msg=f"Failed to create VPC pair {nrm.current_identifier}: {str(e)}",
            fabric=fabric_name,
            switch_id=switch_id,
            peer_switch_id=peer_switch_id,
            path=path,
            exception_type=type(e).__name__
        )


def custom_vpc_update(nrm) -> Optional[Dict[str, Any]]:
    """
    Custom update function for VPC pairs using RestSend.

    - Uses PUT with discriminator (same as create)
    - Validates switches exist in fabric
    - Checks for switch conflicts
    - Uses DeepDiff to detect if update is actually needed
    - Proper error handling

    Args:
        nrm: NDNetworkResourceModule instance

    Returns:
        API response dictionary or None

    Raises:
        ValueError: If fabric_name or switch_id is not provided
    """
    if nrm.module.check_mode:
        return nrm.proposed_config

    fabric_name = nrm.module.params.get("fabric_name")
    switch_id = nrm.proposed_config.get(VpcPairConstants.FIELD_SWITCH_ID)
    peer_switch_id = nrm.proposed_config.get(VpcPairConstants.FIELD_PEER_SWITCH_ID)

    # Path validation
    if not fabric_name:
        raise ValueError("fabric_name is required but was not provided")
    if not switch_id:
        raise ValueError("switch_id is required but was not provided")
    if not peer_switch_id:
        raise ValueError("peer_switch_id is required but was not provided")

    # Validation Step 1: Check switches exist in fabric (from Common.validate_switches_exist)
    fabric_switches = nrm.module.params.get("_fabric_switches", {})
    if fabric_switches:
        missing_switches = []
        if switch_id not in fabric_switches:
            missing_switches.append(switch_id)
        if peer_switch_id not in fabric_switches:
            missing_switches.append(peer_switch_id)

        if missing_switches:
            valid_switches = sorted(fabric_switches.keys())
            error_msg = (
                f"Switch validation failed: The following switch(es) do not exist in fabric '{fabric_name}':\n"
                f"  Missing switches: {', '.join(missing_switches)}\n"
                f"  Affected vPC pair: {nrm.current_identifier}\n\n"
                f"Please ensure:\n"
                f"  1. Switch serial numbers are correct (not IP addresses)\n"
                f"  2. Switches are discovered and present in the fabric\n"
                f"  3. You have the correct fabric name specified\n\n"
            )

            # Include limited valid switches list for reference
            if len(valid_switches) <= 10:
                error_msg += f"Valid switches in fabric: {', '.join(valid_switches)}"
            else:
                error_msg += f"Valid switches in fabric (first 10): {', '.join(valid_switches[:10])} ... and {len(valid_switches) - 10} more"

            nrm.module.fail_json(
                msg=error_msg,
                missing_switches=missing_switches,
                vpc_pair_key=nrm.current_identifier,
                total_valid_switches=len(valid_switches)
            )
    
    # Validation Step 2: Check for switch conflicts (from Common.validate_no_switch_conflicts)
    have_vpc_pairs = nrm.module.params.get("_have", [])
    if have_vpc_pairs:
        # Filter out the current VPC pair being updated
        other_vpc_pairs = [
            vpc for vpc in have_vpc_pairs 
            if vpc.get(VpcPairConstants.FIELD_SWITCH_ID) != switch_id
        ]
        if other_vpc_pairs:
            _validate_switch_conflicts([nrm.proposed_config], other_vpc_pairs, nrm.module)

    # Validation Step 3: Check if update is actually needed using DeepDiff
    if nrm.existing_config:
        want_dict = nrm.proposed_config.model_dump(by_alias=True, exclude_none=True) if hasattr(nrm.proposed_config, 'model_dump') else nrm.proposed_config
        have_dict = nrm.existing_config.model_dump(by_alias=True, exclude_none=True) if hasattr(nrm.existing_config, 'model_dump') else nrm.existing_config
        
        if not _is_update_needed(want_dict, have_dict):
            # No changes needed - return existing config
            nrm.module.warn(
                f"VPC pair {nrm.current_identifier} is already in desired state - skipping update"
            )
            return nrm.existing_config

    # Initialize RestSend via NDModuleV2
    nd_v2 = NDModuleV2(nrm.module)

    # Build path with switch ID
    path = VpcPairEndpoints.vpc_pair_put(fabric_name, switch_id)

    # Build payload with discriminator using helper (supports vpc_pair_details)
    payload = _build_vpc_pair_payload(nrm.proposed_config)

    # Log the operation
    nrm.format_log(
        identifier=nrm.current_identifier,
        status="updated",
        after_data=payload,
        sent_payload_data=payload
    )

    try:
        # Use PUT for update via RestSend
        response = nd_v2.request(path, HttpVerbEnum.PUT, payload)
        return response

    except NDModuleError as error:
        nrm.module.fail_json(
            msg=f"Failed to update VPC pair {nrm.current_identifier}: {error.msg}",
            fabric=fabric_name,
            switch_id=switch_id,
            path=path,
            status=error.status,
            **error.to_dict()
        )
    except Exception as e:
        nrm.module.fail_json(
            msg=f"Failed to update VPC pair {nrm.current_identifier}: {str(e)}",
            fabric=fabric_name,
            switch_id=switch_id,
            path=path,
            exception_type=type(e).__name__
        )


def custom_vpc_delete(nrm) -> None:
    """
    Custom delete function for VPC pairs using RestSend with PUT + discriminator.

    - Pre-deletion validation (network/VRF/interface checks)
    - Uses PUT instead of DELETE (non-RESTful API)
    - Adds vpcAction: "unpair" discriminator
    - Proper error handling with NDModuleError

    Args:
        nrm: NDNetworkResourceModule instance

    Raises:
        ValueError: If fabric_name or switch_id is not provided
        AnsibleModule.fail_json: If validation fails (networks/VRFs attached)
    """
    if nrm.module.check_mode:
        return

    fabric_name = nrm.module.params.get("fabric_name")
    switch_id = nrm.existing_config.get(VpcPairConstants.FIELD_SWITCH_ID)
    peer_switch_id = nrm.existing_config.get(VpcPairConstants.FIELD_PEER_SWITCH_ID)

    # Path validation
    if not fabric_name:
        raise ValueError("fabric_name is required but was not provided")
    if not switch_id:
        raise ValueError("switch_id is required but was not provided")

    # Initialize RestSend via NDModuleV2
    nd_v2 = NDModuleV2(nrm.module)

    # CRITICAL: Pre-deletion validation to prevent data loss
    # Checks for active networks, VRFs, and warns about vPC interfaces
    vpc_pair_key = f"{switch_id}-{peer_switch_id}" if peer_switch_id else switch_id
    _validate_vpc_pair_deletion(nd_v2, fabric_name, switch_id, vpc_pair_key, nrm.module)

    # Build path with switch ID
    path = VpcPairEndpoints.vpc_pair_put(fabric_name, switch_id)

    # Build minimal payload with discriminator for delete
    payload = {
        VpcPairConstants.VPC_ACTION: VpcPairConstants.VPC_ACTION_UNPAIR,  # ← Discriminator for DELETE
        VpcPairConstants.FIELD_SWITCH_ID: nrm.existing_config.get(VpcPairConstants.FIELD_SWITCH_ID),
        VpcPairConstants.FIELD_PEER_SWITCH_ID: nrm.existing_config.get(VpcPairConstants.FIELD_PEER_SWITCH_ID)
    }

    # Log the operation
    nrm.format_log(
        identifier=nrm.current_identifier,
        status="deleted",
        sent_payload_data=payload
    )

    try:
        # Use PUT (not DELETE!) for unpair via RestSend
        nd_v2.request(path, HttpVerbEnum.PUT, payload)

    except NDModuleError as error:
        nrm.module.fail_json(
            msg=f"Failed to delete VPC pair {nrm.current_identifier}: {error.msg}",
            fabric=fabric_name,
            switch_id=switch_id,
            path=path,
            status=error.status,
            **error.to_dict()
        )
    except Exception as e:
        nrm.module.fail_json(
            msg=f"Failed to delete VPC pair {nrm.current_identifier}: {str(e)}",
            fabric=fabric_name,
            switch_id=switch_id,
            path=path,
            exception_type=type(e).__name__
        )


def _needs_deployment(result: Dict, nrm) -> bool:
    """
    Determine if deployment is needed based on changes and pending operations.
    
    Deployment is needed if any of:
    1. There are items in the diff (configuration changes)
    2. There are pending create VPC pairs
    3. There are pending delete VPC pairs
    
    Args:
        result: Module result dictionary with diff info
        nrm: NDNetworkResourceModule instance
        
    Returns:
        True if deployment is needed, False otherwise
    """
    # Check if there are any changes in the result
    has_changes = result.get("changed", False)
    
    # Check diff - framework stores before/after
    before = result.get("before", [])
    after = result.get("after", [])
    has_diff_changes = before != after
    
    # Check pending operations
    pending_create = nrm.module.params.get("_pending_create", [])
    pending_delete = nrm.module.params.get("_pending_delete", [])
    has_pending = bool(pending_create or pending_delete)
    
    needs_deploy = has_changes or has_diff_changes or has_pending
    
    return needs_deploy


def custom_vpc_deploy(nrm, fabric_name: str, result: Dict) -> Dict[str, Any]:
    """
    Custom deploy function for fabric configuration changes using RestSend.

    - Smart deployment decision (Common.needs_deployment)
    - Step 1: Save fabric configuration
    - Step 2: Deploy fabric with forceShowRun=true
    - Proper error handling with NDModuleError
    - Results aggregation
    - Only deploys if there are actual changes or pending operations

    Args:
        nrm: NDNetworkResourceModule instance
        fabric_name: Fabric name to deploy
        result: Module result dictionary to check for changes

    Returns:
        Deployment result dictionary

    Raises:
        NDModuleError: If deployment fails
    """
    # Smart deployment decision (from Common.needs_deployment)
    if not _needs_deployment(result, nrm):
        return {
            "msg": "No configuration changes or pending operations detected, skipping deployment",
            "fabric": fabric_name,
            "deployment_needed": False,
            "changed": False
        }
    
    if nrm.module.check_mode:
        # Dry run deployment info (similar to show_dry_run_deployment_info)
        before = result.get("before", [])
        after = result.get("after", [])
        pending_create = nrm.module.params.get("_pending_create", [])
        pending_delete = nrm.module.params.get("_pending_delete", [])
        
        deployment_info = {
            "msg": "CHECK MODE: Would save and deploy fabric configuration",
            "fabric": fabric_name,
            "deployment_needed": True,
            "changed": True,
            "would_deploy": True,
            "deployment_decision_factors": {
                "diff_has_changes": before != after,
                "pending_create_operations": len(pending_create),
                "pending_delete_operations": len(pending_delete),
                "actual_changes": result.get("changed", False)
            },
            "planned_actions": [
                f"POST {VpcPairEndpoints.fabric_config_save(fabric_name)}",
                f"POST {VpcPairEndpoints.fabric_config_deploy(fabric_name, force_show_run=True)}"
            ]
        }
        return deployment_info

    # Initialize RestSend via NDModuleV2
    nd_v2 = NDModuleV2(nrm.module)
    results = Results()

    # Step 1: Save config
    save_path = VpcPairEndpoints.fabric_config_save(fabric_name)

    try:
        nd_v2.request(save_path, HttpVerbEnum.POST, {})

        results.response_current = {
            "RETURN_CODE": nd_v2.status,
            "METHOD": "POST",
            "REQUEST_PATH": save_path,
            "MESSAGE": "Config saved successfully",
            "DATA": {},
        }
        results.result_current = {"success": True, "changed": True}
        results.register_task_result()

    except NDModuleError as error:
        # Log warning but continue to deploy
        nrm.module.warn(f"Config save failed: {error.msg}")

        results.response_current = {
            "RETURN_CODE": error.status if error.status else -1,
            "MESSAGE": error.msg,
            "REQUEST_PATH": save_path,
            "METHOD": "POST",
            "DATA": {},
        }
        results.result_current = {"success": False, "changed": False}
        results.register_task_result()

    # Step 2: Deploy
    deploy_path = VpcPairEndpoints.fabric_config_deploy(fabric_name, force_show_run=True)

    try:
        nd_v2.request(deploy_path, HttpVerbEnum.POST, {})

        results.response_current = {
            "RETURN_CODE": nd_v2.status,
            "METHOD": "POST",
            "REQUEST_PATH": deploy_path,
            "MESSAGE": "Deployment successful",
            "DATA": {},
        }
        results.result_current = {"success": True, "changed": True}
        results.register_task_result()

    except NDModuleError as error:
        results.response_current = {
            "RETURN_CODE": error.status if error.status else -1,
            "MESSAGE": error.msg,
            "REQUEST_PATH": deploy_path,
            "METHOD": "POST",
            "DATA": {},
        }
        results.result_current = {"success": False, "changed": False}
        results.register_task_result()

        # Build final result and fail
        results.build_final_result()
        nrm.module.fail_json(**results.final_result)

    # Build final result
    results.build_final_result()
    return results.final_result


# ===== Module Entry Point =====


def main():
    """
    Module entry point combining framework + RestSend.

    Architecture:
    - NDNetworkResourceModule framework handles state management
    - Custom actions use RestSend (NDModuleV2) for HTTP with retry logic
    - actions_overwrite_map provides the integration glue
    """
    argument_spec = dict(
        state=dict(
            type="str",
            default="merged",
            choices=["merged", "replaced", "deleted", "overridden", "gathered"],
        ),
        fabric_name=dict(type="str", required=True),
        deploy=dict(type="bool", default=False),
        dry_run=dict(type="bool", default=False),
        config=dict(
            type="list",
            elements="dict",
            options=dict(
                peer1_switch_id=dict(type="str", required=True, aliases=["switch_id"]),
                peer2_switch_id=dict(type="str", required=True, aliases=["peer_switch_id"]),
                use_virtual_peer_link=dict(type="bool", default=True),
            ),
        ),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    # Module-level validations
    if sys.version_info < (3, 9):
        module.fail_json(msg="Python version 3.9 or higher is required for this module.")

    if not HAS_DEEPDIFF:
        module.fail_json(
            msg=missing_required_lib("deepdiff"),
            exception=DEEPDIFF_IMPORT_ERROR
        )

    # State-specific parameter validations
    state = module.params.get("state")
    deploy = module.params.get("deploy")
    dry_run = module.params.get("dry_run")

    if state == "gathered" and deploy:
        module.fail_json(msg="Deploy parameter cannot be used with 'gathered' state")

    if state == "gathered" and dry_run:
        module.fail_json(msg="Dry_run parameter cannot be used with 'gathered' state")

    # Map dry_run to check_mode
    if dry_run:
        module.check_mode = True

    # Normalize config keys for model
    config = module.params.get("config") or []
    normalized_config = []

    for item in config:
        normalized = {
            "switch_id": item.get("peer1_switch_id") or item.get("switch_id"),
            "peer_switch_id": item.get("peer2_switch_id") or item.get("peer_switch_id"),
            "use_virtual_peer_link": item.get("use_virtual_peer_link", True),
        }
        normalized_config.append(normalized)

    module.params["config"] = normalized_config

    # ============================================================
    # ACTIONS OVERWRITE MAP - Integration of Framework + RestSend
    # ============================================================
    # This is where we override default framework behaviors to:
    # 1. Use RestSend (NDModuleV2) for HTTP with retry logic
    # 2. Handle non-RESTful API (PUT for create/delete)
    # 3. Add discriminator pattern (vpcAction field)

    actions_overwrite_map = {
        "query_all": custom_vpc_query_all,  # RestSend query with IP-to-SN mapping
        "create": custom_vpc_create,        # RestSend PUT with vpcAction="pair"
        "update": custom_vpc_update,        # RestSend PUT with vpcAction="pair"
        "delete": custom_vpc_delete,        # RestSend PUT with vpcAction="unpair"
    }

    # Build base path (framework will use custom functions to modify it)
    fabric_name = module.params.get("fabric_name")
    base_path = VpcPairEndpoints.vpc_pair_base(fabric_name)

    try:
        # Create NDNetworkResourceModule instance with custom actions
        nd_vpc_pair = NDNetworkResourceModule(
            module=module,
            path=base_path,
            model_class=VpcPairModel,
            actions_overwrite_map=actions_overwrite_map,  # ← Magic happens here!
        )

        # Run the framework - it will use OUR custom functions with RestSend!
        result = nd_vpc_pair.run()

        # Add IP-to-SN mapping if available
        if "_ip_to_sn_mapping" in module.params:
            result["ip_to_sn_mapping"] = module.params["_ip_to_sn_mapping"]

        # Handle deployment if requested
        deploy = module.params.get("deploy", False)
        if deploy and result.get("changed") and not module.check_mode:
            # Pass result to smart deployment function
            deploy_result = custom_vpc_deploy(nd_vpc_pair, fabric_name, result)

            # Merge deployment results
            result["deployment"] = deploy_result
            if deploy_result.get("failed"):
                result["failed"] = True
                result["changed"] = True  # Still changed even if deploy failed
            
            # Add deployment_needed flag for visibility
            result["deployment_needed"] = deploy_result.get("deployment_needed", True)

        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
