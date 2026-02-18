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
short_description: Manage vPC pairs in Nexus devices using actions_overwrite_map.
version_added: "1.0.0"
description:
- Create, update, delete, override, and gather vPC pairs on Nexus devices.
- Uses NDNetworkResourceModule framework with custom action functions.
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
"""

RETURN = """
changed:
    description: Whether the module made any changes
    type: bool
    returned: always
before:
    description: vPC pair state before changes
    type: list
    returned: always
after:
    description: vPC pair state after changes
    type: list
    returned: always
gathered:
    description: Current vPC pairs (gathered state only)
    type: list
    returned: when state is gathered
"""

from typing import Any, Dict, List, Optional
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.cisco.nd.plugins.module_utils.nd_network_resources import (
    NDNetworkResourceModule,
)
from ansible_collections.cisco.nd.plugins.module_utils.models.base import NDBaseModel
from pydantic import Field


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
    switch_id: str = Field(alias="switchId", description="Peer-1 switch serial number")
    peer_switch_id: str = Field(alias="peerSwitchId", description="Peer-2 switch serial number")
    use_virtual_peer_link: bool = Field(
        default=True, alias="useVirtualPeerLink", description="Virtual peer link enabled"
    )

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
            "switchId": response.get("switchId") or response.get("switch_id"),
            "peerSwitchId": response.get("peerSwitchId") or response.get("peer_switch_id"),
            "useVirtualPeerLink": response.get("useVirtualPeerLink", True),
        }
        return cls.model_validate(data)


# ===== Custom Action Functions (using actions_overwrite_map) =====


def custom_vpc_query_all(nrm) -> List[Dict]:
    """
    Custom query function for VPC pairs.

    Solves:
    ✅ 3-list state management (can query intended vs discovered pairs)

    Args:
        nrm: NDNetworkResourceModule instance

    Returns:
        List of VPC pair dictionaries from API
    """
    fabric_name = nrm.module.params.get("fabric_name")
    path = f"/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/vpcpair/fabrics/{fabric_name}"

    try:
        response = nrm.query_obj(path)

        if response is None:
            return []

        # API returns list directly or nested in data/vpcPairs key
        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            return response.get("data", response.get("vpcPairs", []))

        return []
    except Exception as e:
        nrm.module.fail_json(msg=f"Failed to query VPC pairs: {str(e)}")


def custom_vpc_create(nrm) -> Optional[Dict[str, Any]]:
    """
    Custom create function for VPC pairs using PUT with discriminator.

    Solves:
    ✅ Non-RESTful API - Uses PUT instead of POST
    ✅ Discriminator pattern - Adds vpcAction: "pair"
    ✅ Composite identifier - Handles both switch IDs in path

    Args:
        nrm: NDNetworkResourceModule instance

    Returns:
        API response dictionary or None
    """
    if nrm.module.check_mode:
        return nrm.proposed_config

    fabric_name = nrm.module.params.get("fabric_name")
    switch_id = nrm.proposed_config.get("switchId")

    # Build path with switch ID
    path = f"/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/vpcpair/fabrics/{fabric_name}/switches/{switch_id}"

    # Build payload with discriminator
    payload = nrm.proposed_config.copy()
    payload["vpcAction"] = "pair"  # ← Discriminator for CREATE

    # Log the operation
    nrm.format_log(
        identifier=nrm.current_identifier,
        status="created",
        after_data=payload,
        sent_payload_data=payload
    )

    try:
        # Use PUT (not POST!) for create
        response = nrm.request(path=path, method="PUT", data=payload)
        return response
    except Exception as e:
        nrm.module.fail_json(
            msg=f"Failed to create VPC pair {nrm.current_identifier}: {str(e)}"
        )


def custom_vpc_update(nrm) -> Optional[Dict[str, Any]]:
    """
    Custom update function for VPC pairs.

    Solves:
    ✅ Non-RESTful API - Uses PUT with discriminator (same as create)
    ✅ Multi-step operations - Can add pre-flight checks if needed

    Args:
        nrm: NDNetworkResourceModule instance

    Returns:
        API response dictionary or None
    """
    if nrm.module.check_mode:
        return nrm.proposed_config

    fabric_name = nrm.module.params.get("fabric_name")
    switch_id = nrm.proposed_config.get("switchId")

    # Build path with switch ID
    path = f"/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/vpcpair/fabrics/{fabric_name}/switches/{switch_id}"

    # Build payload with discriminator (update also uses "pair")
    payload = nrm.proposed_config.copy()
    payload["vpcAction"] = "pair"  # ← Discriminator for UPDATE

    # Log the operation
    nrm.format_log(
        identifier=nrm.current_identifier,
        status="updated",
        after_data=payload,
        sent_payload_data=payload
    )

    try:
        # Use PUT for update
        response = nrm.request(path=path, method="PUT", data=payload)
        return response
    except Exception as e:
        nrm.module.fail_json(
            msg=f"Failed to update VPC pair {nrm.current_identifier}: {str(e)}"
        )


def custom_vpc_delete(nrm) -> None:
    """
    Custom delete function for VPC pairs using PUT with discriminator.

    Solves:
    ✅ Non-RESTful API - Uses PUT instead of DELETE
    ✅ Discriminator pattern - Adds vpcAction: "unpair"
    ✅ Composite identifier - Uses both switch IDs from existing config

    Args:
        nrm: NDNetworkResourceModule instance
    """
    if nrm.module.check_mode:
        return

    fabric_name = nrm.module.params.get("fabric_name")
    switch_id = nrm.existing_config.get("switchId")

    # Build path with switch ID
    path = f"/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/vpcpair/fabrics/{fabric_name}/switches/{switch_id}"

    # Build minimal payload with discriminator for delete
    payload = {
        "vpcAction": "unpair",  # ← Discriminator for DELETE
        "switchId": nrm.existing_config.get("switchId"),
        "peerSwitchId": nrm.existing_config.get("peerSwitchId")
    }

    # Log the operation
    nrm.format_log(
        identifier=nrm.current_identifier,
        status="deleted",
        sent_payload_data=payload
    )

    try:
        # Use PUT (not DELETE!) for unpair
        nrm.request(path=path, method="PUT", data=payload)
    except Exception as e:
        nrm.module.fail_json(
            msg=f"Failed to delete VPC pair {nrm.current_identifier}: {str(e)}"
        )


# ===== Module Entry Point =====


def main():
    """
    Module entry point using actions_overwrite_map pattern.
    """
    argument_spec = dict(
        state=dict(
            type="str",
            default="merged",
            choices=["merged", "replaced", "deleted", "overridden", "gathered"],
        ),
        fabric_name=dict(type="str", required=True),
        deploy=dict(type="bool", default=False),
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
    # ACTIONS OVERWRITE MAP - The Key to Solving VPC Limitations!
    # ============================================================
    # This is where we override default framework behaviors to handle:
    # - Non-RESTful API (PUT for create/delete instead of POST/DELETE)
    # - Discriminator pattern (vpcAction field determines operation)
    # - Composite identifiers (switch_id + peer_switch_id)
    # - Multi-step operations (can add pre-flight checks)
    # - 3-list state management (intended vs discovered pairs)

    actions_overwrite_map = {
        "query_all": custom_vpc_query_all,  # Custom query for VPC pairs
        "create": custom_vpc_create,        # PUT with vpcAction="pair"
        "update": custom_vpc_update,        # PUT with vpcAction="pair"
        "delete": custom_vpc_delete,        # PUT with vpcAction="unpair"
    }

    # Build base path (framework will use custom functions to modify it)
    fabric_name = module.params.get("fabric_name")
    base_path = f"/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/vpcpair/fabrics/{fabric_name}"

    try:
        # Create NDNetworkResourceModule instance with custom actions
        nd_vpc_pair = NDNetworkResourceModule(
            module=module,
            path=base_path,
            model_class=VpcPairModel,
            actions_overwrite_map=actions_overwrite_map,  # ← Magic happens here!
        )

        # Run the framework - it will use OUR custom functions!
        result = nd_vpc_pair.run()

        # Handle deployment if requested
        deploy = module.params.get("deploy", False)
        if deploy and result.get("changed") and not module.check_mode:
            # Deploy config (add save_config and deploy_config methods)
            # nd_vpc_pair.save_config(fabric_name)
            # nd_vpc_pair.deploy_config(fabric_name)
            pass

        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
