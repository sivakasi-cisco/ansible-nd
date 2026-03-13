# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Sivakami S <sivakasi@cisco.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

from typing import Any, Dict

from ansible_collections.cisco.nd.plugins.module_utils.endpoints.v1.manage_vpc_pair.enums import (
    VpcFieldNames,
)
from ansible_collections.cisco.nd.plugins.module_utils.nd_manage_vpc_pair_common import (
    _collection_to_list_flex,
)

def run_vpc_module(nrm) -> Dict[str, Any]:
    """
    Run VPC module state machine with VPC-specific gathered output.

    gathered is the query/read-only mode for VPC pairs.
    """
    state = nrm.module.params.get("state", "merged")
    config = nrm.module.params.get("config", [])

    if state == "gathered":
        nrm.add_logs_and_outputs()
        nrm.result["changed"] = False

        current_pairs = nrm.result.get("current", []) or []
        pending_delete = nrm.module.params.get("_pending_delete", []) or []

        # Exclude pairs in pending-delete from active gathered set.
        pending_delete_keys = set()
        for pair in pending_delete:
            switch_id = pair.get(VpcFieldNames.SWITCH_ID) or pair.get("switch_id")
            peer_switch_id = pair.get(VpcFieldNames.PEER_SWITCH_ID) or pair.get("peer_switch_id")
            if switch_id and peer_switch_id:
                pending_delete_keys.add(tuple(sorted([switch_id, peer_switch_id])))

        filtered_current = []
        for pair in current_pairs:
            switch_id = pair.get(VpcFieldNames.SWITCH_ID) or pair.get("switch_id")
            peer_switch_id = pair.get(VpcFieldNames.PEER_SWITCH_ID) or pair.get("peer_switch_id")
            if switch_id and peer_switch_id:
                pair_key = tuple(sorted([switch_id, peer_switch_id]))
                if pair_key in pending_delete_keys:
                    continue
            filtered_current.append(pair)

        nrm.result["current"] = filtered_current
        nrm.result["gathered"] = {
            "vpc_pairs": filtered_current,
            "pending_create_vpc_pairs": nrm.module.params.get("_pending_create", []),
            "pending_delete_vpc_pairs": pending_delete,
        }
        return nrm.result

    # state=deleted with empty config means "delete all existing pairs in this fabric".
    #
    # state=overridden with empty config has the same user intent (TC4):
    # remove all existing pairs from this fabric.
    if state in ("deleted", "overridden") and not config:
        # Use the live existing collection from NDStateMachine.
        # nrm.result["current"] is only populated after add_logs_and_outputs(), so relying on
        # it here would incorrectly produce an empty delete list.
        existing_pairs = _collection_to_list_flex(getattr(nrm, "existing", None))
        if not existing_pairs:
            existing_pairs = nrm.result.get("current", []) or []

        delete_all_config = []
        for pair in existing_pairs:
            switch_id = pair.get(VpcFieldNames.SWITCH_ID) or pair.get("switch_id")
            peer_switch_id = pair.get(VpcFieldNames.PEER_SWITCH_ID) or pair.get("peer_switch_id")
            if switch_id and peer_switch_id:
                use_vpl = pair.get(VpcFieldNames.USE_VIRTUAL_PEER_LINK)
                if use_vpl is None:
                    use_vpl = pair.get("use_virtual_peer_link", True)
                delete_all_config.append(
                    {
                        "switch_id": switch_id,
                        "peer_switch_id": peer_switch_id,
                        "use_virtual_peer_link": use_vpl,
                    }
                )
        config = delete_all_config
        # Force explicit delete operations instead of relying on overridden-state
        # reconciliation behavior with empty desired config.
        if state == "overridden":
            state = "deleted"

    nrm.manage_state(state=state, new_configs=config)
    nrm.add_logs_and_outputs()
    return nrm.result


# ===== Module Entry Point =====


