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
- Supports state-based operations with intelligent diff calculation.
- Uses NDNetworkResourceModule framework for Want/Have/Need logic.
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


# ===== VPC Pair Model (using new framework) =====


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
        Convert to VPC pairing API payload.

        The API expects vpcAction="pair" for create/update operations.
        """
        payload = self.model_dump(by_alias=True, exclude_none=True)
        payload["vpcAction"] = "pair"
        return payload

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> "VpcPairModel":
        """
        Parse VPC pair from API response.

        Handles API field name variations.
        """
        # Map API response fields to model fields
        data = {
            "switchId": response.get("switchId") or response.get("switch_id"),
            "peerSwitchId": response.get("peerSwitchId") or response.get("peer_switch_id"),
            "useVirtualPeerLink": response.get("useVirtualPeerLink", True),
        }
        return cls.model_validate(data)


# ===== VPC Pair Module (using framework) =====


class VpcPairModule(NDNetworkResourceModule[VpcPairModel]):
    """
    Module for managing VPC pairs using NDNetworkResourceModule framework.

    API Endpoints:
    - GET:    /appcenter/cisco/ndfc/api/v1/lan-fabric/rest/vpcpair/fabrics/{fabric}
    - POST:   /appcenter/cisco/ndfc/api/v1/lan-fabric/rest/vpcpair/fabrics/{fabric}/switches/{switchId}
    - PUT:    /appcenter/cisco/ndfc/api/v1/lan-fabric/rest/vpcpair/fabrics/{fabric}/switches/{switchId}
    - DELETE: Uses PUT with vpcAction="unpair"
    """

    model_class = VpcPairModel

    # VPC pairs use these fields for comparison - ignore dynamic fields
    diff_ignore_keys = ["vpcPairDetails", "operStatus", "timestamp"]

    def __init__(self, module: AnsibleModule):
        super().__init__(module)
        self.fabric_name = module.params.get("fabric_name")
        self.deploy = module.params.get("deploy", False)

    def _get_base_path(self) -> str:
        """Get base API path for VPC pairs."""
        return f"/appcenter/cisco/ndfc/api/v1/lan-fabric/rest/vpcpair/fabrics/{self.fabric_name}"

    def _get_item_path(self, identifier: Any) -> str:
        """Get API path for a specific VPC pair.

        Args:
            identifier: Tuple of (switch_id, peer_switch_id)
        """
        switch_id = identifier[0] if isinstance(identifier, tuple) else identifier
        return f"{self._get_base_path()}/switches/{switch_id}"

    def _query_all(self) -> List[Dict]:
        """Query all existing VPC pairs."""
        path = self._get_base_path()
        response = self.request(path, method="GET")

        if response is None:
            return []

        # API returns list directly or nested in data key
        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            return response.get("data", response.get("vpcPairs", []))

        return []

    def _create(self, item: VpcPairModel) -> bool:
        """Create a new VPC pair via POST."""
        switch_id = item.switch_id
        path = f"{self._get_base_path()}/switches/{switch_id}"
        payload = item.to_payload()

        self._results["commands"].append({"action": "pair", "path": path, "payload": payload})

        if not self.module.check_mode:
            response = self.request(path, method="POST", data=payload)
            if response is None or (isinstance(response, dict) and response.get("error")):
                self.module.fail_json(
                    msg=f"Failed to create VPC pair {item.switch_id}-{item.peer_switch_id}: {response}"
                )

        return True

    def _update(self, have_item: VpcPairModel, want_item: VpcPairModel) -> bool:
        """Update an existing VPC pair via PUT."""
        switch_id = want_item.switch_id
        path = f"{self._get_base_path()}/switches/{switch_id}"
        payload = want_item.to_payload()

        self._results["commands"].append(
            {
                "action": "update",
                "path": path,
                "payload": payload,
                "previous": have_item.to_diff_dict(),
            }
        )

        if not self.module.check_mode:
            response = self.request(path, method="PUT", data=payload)
            if response is None or (isinstance(response, dict) and response.get("error")):
                self.module.fail_json(
                    msg=f"Failed to update VPC pair {want_item.switch_id}-{want_item.peer_switch_id}: {response}"
                )

        return True

    def _delete(self, item: VpcPairModel) -> bool:
        """Delete a VPC pair (send unpair action via PUT)."""
        switch_id = item.switch_id
        path = f"{self._get_base_path()}/switches/{switch_id}"

        # NDFC uses PUT with vpcAction="unpair" for deletion
        payload = {"vpcAction": "unpair"}

        self._results["commands"].append(
            {"action": "unpair", "path": path, "payload": payload, "item": item.to_diff_dict()}
        )

        if not self.module.check_mode:
            response = self.request(path, method="PUT", data=payload)
            if response is None or (isinstance(response, dict) and response.get("error")):
                self.module.fail_json(
                    msg=f"Failed to delete VPC pair {item.switch_id}-{item.peer_switch_id}: {response}"
                )

        return True

    def manage_state(self) -> Dict[str, Any]:
        """Override to add deploy step."""
        result = super().manage_state()

        # Deploy if requested and changes were made
        if self.deploy and result.get("changed") and not self.module.check_mode:
            self.save_config(self.fabric_name)
            self.deploy_config(self.fabric_name)

        return result


# ===== Module Entry Point =====


def main():
    """Module entry point."""
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

    try:
        vpc_module = VpcPairModule(module)
        result = vpc_module.manage_state()
        module.exit_json(**result)
    except Exception as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
