# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Sivakami S <sivakasi@cisco.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

from typing import Any, Dict, List, Optional

from ansible_collections.cisco.nd.plugins.module_utils.enums import HttpVerbEnum
from ansible_collections.cisco.nd.plugins.module_utils.endpoints.v1.manage.vpc_pair_enums import (
    VpcFieldNames,
)
from ansible_collections.cisco.nd.plugins.module_utils.nd_manage_vpc_pair_validation import (
    _is_switch_in_vpc_pair,
    _validate_fabric_switches,
)
from ansible_collections.cisco.nd.plugins.module_utils.endpoints.v1.manage.vpc_pair_runtime_endpoints import (
    VpcPairEndpoints,
)
from ansible_collections.cisco.nd.plugins.module_utils.endpoints.v1.manage.vpc_pair_runtime_payloads import (
    _get_api_field_value,
)
from ansible_collections.cisco.nd.plugins.module_utils.nd_v2 import (
    NDModule as NDModuleV2,
    NDModuleError,
)

def _get_recommendation_details(nd_v2, fabric_name: str, switch_id: str, timeout: Optional[int] = None) -> Optional[Dict]:
    """
    Get VPC pair recommendation details from ND for a specific switch.

    Returns peer switch info and useVirtualPeerLink status.

    Args:
        nd_v2: NDModuleV2 instance for RestSend
        fabric_name: Fabric name
        switch_id: Switch serial number
        timeout: Optional timeout override (uses module param if not specified)

    Returns:
        Dict with peer info or None if not found (404)

    Raises:
        NDModuleError: On API errors other than 404 (timeouts, 500s, etc.)
    """
    # Validate inputs to prevent injection
    if not fabric_name or not isinstance(fabric_name, str):
        raise ValueError(f"Invalid fabric_name: {fabric_name}")
    if not switch_id or not isinstance(switch_id, str) or len(switch_id) < 3:
        raise ValueError(f"Invalid switch_id: {switch_id}")

    try:
        path = VpcPairEndpoints.switch_vpc_recommendations(fabric_name, switch_id)

        # Use query timeout from module params or override
        if timeout is None:
            timeout = nd_v2.module.params.get("query_timeout", 10)

        rest_send = nd_v2._get_rest_send()
        rest_send.save_settings()
        rest_send.timeout = timeout
        try:
            vpc_recommendations = nd_v2.request(path, HttpVerbEnum.GET)
        finally:
            rest_send.restore_settings()

        if vpc_recommendations is None or vpc_recommendations == {}:
            return None

        # Validate response structure and look for current peer
        if isinstance(vpc_recommendations, list):
            for sw in vpc_recommendations:
                # Validate each entry
                if not isinstance(sw, dict):
                    nd_v2.module.warn(
                        f"Skipping invalid recommendation entry for switch {switch_id}: "
                        f"expected dict, got {type(sw).__name__}"
                    )
                    continue

                # Check for current peer indicators
                if sw.get(VpcFieldNames.CURRENT_PEER) or sw.get(VpcFieldNames.IS_CURRENT_PEER):
                    # Validate required fields exist
                    if VpcFieldNames.SERIAL_NUMBER not in sw:
                        nd_v2.module.warn(
                            f"Recommendation missing serialNumber field for switch {switch_id}"
                        )
                        continue
                    return sw
        elif vpc_recommendations:
            # Unexpected response format
            nd_v2.module.warn(
                f"Unexpected recommendation response format for switch {switch_id}: "
                f"expected list, got {type(vpc_recommendations).__name__}"
            )

        return None
    except NDModuleError as error:
        # Handle expected error codes gracefully
        if error.status == 404:
            # No recommendations exist (expected for switches without VPC)
            return None
        elif error.status == 500:
            # Server error - recommendation API may be unstable
            # Treat as "no recommendations available" to allow graceful degradation
            nd_v2.module.warn(
                f"VPC recommendation API returned 500 error for switch {switch_id} - "
                f"treating as no recommendations available"
            )
            return None
        # Let other errors (timeouts, rate limits) propagate
        raise


def _extract_vpc_pairs_from_list_response(vpc_pairs_response: Any) -> List[Dict[str, Any]]:
    """
    Extract VPC pair list entries from /vpcPairs response payload.

    Supports common response wrappers used by ND API.
    """
    if not isinstance(vpc_pairs_response, dict):
        return []

    candidates = None
    for key in (VpcFieldNames.VPC_PAIRS, "items", VpcFieldNames.DATA):
        value = vpc_pairs_response.get(key)
        if isinstance(value, list):
            candidates = value
            break

    if not isinstance(candidates, list):
        return []

    extracted_pairs = []
    for item in candidates:
        if not isinstance(item, dict):
            continue

        switch_id = item.get(VpcFieldNames.SWITCH_ID)
        peer_switch_id = item.get(VpcFieldNames.PEER_SWITCH_ID)

        # Handle alternate response shape if switch IDs are nested under "switch"/"peerSwitch"
        if isinstance(switch_id, dict) and isinstance(peer_switch_id, dict):
            switch_id = switch_id.get("switch")
            peer_switch_id = peer_switch_id.get("peerSwitch")

        if not switch_id or not peer_switch_id:
            continue

        extracted_pairs.append(
            {
                VpcFieldNames.SWITCH_ID: switch_id,
                VpcFieldNames.PEER_SWITCH_ID: peer_switch_id,
                VpcFieldNames.USE_VIRTUAL_PEER_LINK: item.get(
                    VpcFieldNames.USE_VIRTUAL_PEER_LINK, True
                ),
            }
        )

    return extracted_pairs


def _enrich_pairs_from_direct_vpc(
    nd_v2,
    fabric_name: str,
    pairs: List[Dict[str, Any]],
    timeout: int = 5,
) -> List[Dict[str, Any]]:
    """
    Enrich pair fields from per-switch /vpcPair endpoint when available.

    The /vpcPairs list response may omit fields like useVirtualPeerLink.
    This helper preserves lightweight list discovery while improving field
    accuracy for gathered output.
    """
    if not pairs:
        return []

    enriched_pairs: List[Dict[str, Any]] = []
    for pair in pairs:
        enriched = dict(pair)
        switch_id = enriched.get(VpcFieldNames.SWITCH_ID)
        if not switch_id:
            enriched_pairs.append(enriched)
            continue

        direct_vpc = None
        path = VpcPairEndpoints.switch_vpc_pair(fabric_name, switch_id)
        rest_send = nd_v2._get_rest_send()
        rest_send.save_settings()
        rest_send.timeout = timeout
        try:
            direct_vpc = nd_v2.request(path, HttpVerbEnum.GET)
        except (NDModuleError, Exception):
            direct_vpc = None
        finally:
            rest_send.restore_settings()

        if isinstance(direct_vpc, dict):
            peer_switch_id = direct_vpc.get(VpcFieldNames.PEER_SWITCH_ID)
            if peer_switch_id:
                enriched[VpcFieldNames.PEER_SWITCH_ID] = peer_switch_id

            use_virtual_peer_link = _get_api_field_value(
                direct_vpc,
                "useVirtualPeerLink",
                enriched.get(VpcFieldNames.USE_VIRTUAL_PEER_LINK),
            )
            if use_virtual_peer_link is not None:
                enriched[VpcFieldNames.USE_VIRTUAL_PEER_LINK] = use_virtual_peer_link

        enriched_pairs.append(enriched)

    return enriched_pairs


def _filter_stale_vpc_pairs(
    nd_v2,
    fabric_name: str,
    pairs: List[Dict[str, Any]],
    module,
) -> List[Dict[str, Any]]:
    """
    Remove stale pairs using overview membership checks.

    `/vpcPairs` can briefly lag after unpair operations. We perform a lightweight
    best-effort membership check and drop entries that are explicitly reported as
    not part of a vPC pair.
    """
    if not pairs:
        return []

    pruned_pairs: List[Dict[str, Any]] = []
    for pair in pairs:
        switch_id = pair.get(VpcFieldNames.SWITCH_ID)
        if not switch_id:
            pruned_pairs.append(pair)
            continue

        membership = _is_switch_in_vpc_pair(nd_v2, fabric_name, switch_id, timeout=5)
        if membership is False:
            module.warn(
                f"Excluding stale vPC pair entry for switch {switch_id} "
                "because overview reports it is not in a vPC pair."
            )
            continue
        pruned_pairs.append(pair)

    return pruned_pairs


def _filter_vpc_pairs_by_requested_config(
    pairs: List[Dict[str, Any]],
    config: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Filter queried VPC pairs by explicit pair keys provided in gathered config.

    If gathered config is empty or does not contain complete switch pairs, return
    the unfiltered pair list.
    """
    if not pairs or not config:
        return list(pairs or [])

    requested_pair_keys = set()
    for item in config:
        switch_id = item.get("switch_id") or item.get(VpcFieldNames.SWITCH_ID)
        peer_switch_id = item.get("peer_switch_id") or item.get(VpcFieldNames.PEER_SWITCH_ID)
        if switch_id and peer_switch_id:
            requested_pair_keys.add(tuple(sorted([switch_id, peer_switch_id])))

    if not requested_pair_keys:
        return list(pairs)

    filtered_pairs = []
    for item in pairs:
        switch_id = item.get("switch_id") or item.get(VpcFieldNames.SWITCH_ID)
        peer_switch_id = item.get("peer_switch_id") or item.get(VpcFieldNames.PEER_SWITCH_ID)
        if switch_id and peer_switch_id:
            pair_key = tuple(sorted([switch_id, peer_switch_id]))
            if pair_key in requested_pair_keys:
                filtered_pairs.append(item)

    return filtered_pairs


def custom_vpc_query_all(nrm) -> List[Dict]:
    """
    Query existing VPC pairs with state-aware enrichment.

    Flow:
    - Base query from /vpcPairs list (always attempted first)
    - gathered/deleted: use lightweight list-only data when available
    - merged/replaced/overridden: enrich with switch inventory and recommendation
      APIs to build have/pending_create/pending_delete sets
    """
    fabric_name = nrm.module.params.get("fabric_name")

    if not fabric_name or not isinstance(fabric_name, str) or not fabric_name.strip():
        raise ValueError(f"fabric_name must be a non-empty string. Got: {fabric_name!r}")

    state = nrm.module.params.get("state", "merged")
    if state == "gathered":
        config = nrm.module.params.get("_gather_filter_config") or []
    else:
        config = nrm.module.params.get("config") or []

    # Initialize RestSend via NDModuleV2
    nd_v2 = NDModuleV2(nrm.module)

    def _set_lightweight_context(lightweight_have: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        nrm.module.params["_fabric_switches"] = []
        nrm.module.params["_fabric_switches_count"] = 0
        nrm.module.params["_ip_to_sn_mapping"] = {}
        nrm.module.params["_have"] = lightweight_have
        nrm.module.params["_pending_create"] = []
        nrm.module.params["_pending_delete"] = []
        return lightweight_have

    try:
        # Step 1: Base query from list endpoint (/vpcPairs)
        have = []
        list_query_succeeded = False
        try:
            list_path = VpcPairEndpoints.vpc_pairs_list(fabric_name)
            rest_send = nd_v2._get_rest_send()
            rest_send.save_settings()
            rest_send.timeout = nrm.module.params.get("query_timeout", 10)
            try:
                vpc_pairs_response = nd_v2.request(list_path, HttpVerbEnum.GET)
            finally:
                rest_send.restore_settings()
            have.extend(_extract_vpc_pairs_from_list_response(vpc_pairs_response))
            list_query_succeeded = True
        except Exception as list_error:
            nrm.module.warn(
                f"VPC pairs list query failed for fabric {fabric_name}: "
                f"{str(list_error).splitlines()[0]}."
            )

        # Lightweight path for read-only and delete workflows.
        # Keep heavy discovery/enrichment only for write states.
        if state in ("deleted", "gathered"):
            if list_query_succeeded:
                if state == "gathered":
                    have = _filter_vpc_pairs_by_requested_config(have, config)
                    have = _enrich_pairs_from_direct_vpc(
                        nd_v2=nd_v2,
                        fabric_name=fabric_name,
                        pairs=have,
                        timeout=5,
                    )
                have = _filter_stale_vpc_pairs(
                    nd_v2=nd_v2,
                    fabric_name=fabric_name,
                    pairs=have,
                    module=nrm.module,
                )
                return _set_lightweight_context(have)

            nrm.module.warn(
                "Skipping switch-level discovery for read-only/delete workflow because "
                "the vPC list endpoint is unavailable."
            )

            if state == "gathered":
                return _set_lightweight_context([])

            # Preserve explicit delete intent without full-fabric discovery.
            # This keeps delete deterministic and avoids expensive inventory calls.
            fallback_have = []
            for item in config:
                switch_id_val = item.get("switch_id") or item.get(VpcFieldNames.SWITCH_ID)
                peer_switch_id_val = item.get("peer_switch_id") or item.get(VpcFieldNames.PEER_SWITCH_ID)
                if not switch_id_val or not peer_switch_id_val:
                    continue

                use_vpl_val = item.get("use_virtual_peer_link")
                if use_vpl_val is None:
                    use_vpl_val = item.get(VpcFieldNames.USE_VIRTUAL_PEER_LINK, True)

                fallback_have.append(
                    {
                        VpcFieldNames.SWITCH_ID: switch_id_val,
                        VpcFieldNames.PEER_SWITCH_ID: peer_switch_id_val,
                        VpcFieldNames.USE_VIRTUAL_PEER_LINK: use_vpl_val,
                    }
                )

            if fallback_have:
                nrm.module.warn(
                    "Using requested delete config as fallback existing set because "
                    "vPC list query failed."
                )
                return _set_lightweight_context(fallback_have)

            if config:
                nrm.module.warn(
                    "Delete config did not contain complete vPC pairs. "
                    "No delete intents can be built from list-query fallback."
                )
                return _set_lightweight_context([])

            nrm.module.warn(
                "Delete-all requested with no explicit pairs and unavailable list endpoint. "
                "Falling back to switch-level discovery."
            )

        # Step 2 (write-state enrichment): Query and validate fabric switches.
        fabric_switches = _validate_fabric_switches(nd_v2, fabric_name)

        if not fabric_switches:
            nrm.module.warn(f"No switches found in fabric {fabric_name}")
            nrm.module.params["_fabric_switches"] = []
            nrm.module.params["_fabric_switches_count"] = 0
            nrm.module.params["_have"] = []
            nrm.module.params["_pending_create"] = []
            nrm.module.params["_pending_delete"] = []
            return []

        # Keep only switch IDs for validation and serialize safely in module params.
        fabric_switches_list = list(fabric_switches.keys())
        nrm.module.params["_fabric_switches"] = fabric_switches_list
        nrm.module.params["_fabric_switches_count"] = len(fabric_switches)

        # Build IP-to-SN mapping (extract before dict is discarded).
        ip_to_sn = {
            sw.get(VpcFieldNames.FABRIC_MGMT_IP): sw.get(VpcFieldNames.SERIAL_NUMBER)
            for sw in fabric_switches.values()
            if VpcFieldNames.FABRIC_MGMT_IP in sw
        }
        nrm.module.params["_ip_to_sn_mapping"] = ip_to_sn

        # Step 3: Track 3-state VPC pairs (have/pending_create/pending_delete).
        pending_create = []
        pending_delete = []
        processed_switches = set()

        desired_pairs = {}
        config_switch_ids = set()
        for item in config:
            # Config items are normalized to snake_case in main().
            switch_id_val = item.get("switch_id") or item.get(VpcFieldNames.SWITCH_ID)
            peer_switch_id_val = item.get("peer_switch_id") or item.get(VpcFieldNames.PEER_SWITCH_ID)

            if switch_id_val:
                config_switch_ids.add(switch_id_val)
            if peer_switch_id_val:
                config_switch_ids.add(peer_switch_id_val)

            if switch_id_val and peer_switch_id_val:
                desired_pairs[tuple(sorted([switch_id_val, peer_switch_id_val]))] = item

        for switch_id, switch in fabric_switches.items():
            if switch_id in processed_switches:
                continue

            vpc_configured = switch.get(VpcFieldNames.VPC_CONFIGURED, False)
            vpc_data = switch.get("vpcData", {})

            if vpc_configured and vpc_data:
                peer_switch_id = vpc_data.get("peerSwitchId")
                processed_switches.add(switch_id)
                processed_switches.add(peer_switch_id)

                # For configured pairs, prefer direct vPC query as source of truth.
                try:
                    vpc_pair_path = VpcPairEndpoints.switch_vpc_pair(fabric_name, switch_id)
                    rest_send = nd_v2._get_rest_send()
                    rest_send.save_settings()
                    rest_send.timeout = 5
                    try:
                        direct_vpc = nd_v2.request(vpc_pair_path, HttpVerbEnum.GET)
                    finally:
                        rest_send.restore_settings()
                except (NDModuleError, Exception):
                    direct_vpc = None

                if direct_vpc:
                    resolved_peer_switch_id = direct_vpc.get(VpcFieldNames.PEER_SWITCH_ID) or peer_switch_id
                    if resolved_peer_switch_id:
                        processed_switches.add(resolved_peer_switch_id)
                    use_vpl = _get_api_field_value(direct_vpc, "useVirtualPeerLink", False)

                    # Direct /vpcPair can be stale for a short period after delete.
                    # Cross-check overview to avoid reporting stale active pairs.
                    membership = _is_switch_in_vpc_pair(
                        nd_v2, fabric_name, switch_id, timeout=5
                    )
                    if membership is False:
                        pair_key = None
                        if resolved_peer_switch_id:
                            pair_key = tuple(sorted([switch_id, resolved_peer_switch_id]))
                        desired_item = desired_pairs.get(pair_key) if pair_key else None
                        desired_use_vpl = None
                        if desired_item:
                            desired_use_vpl = desired_item.get("use_virtual_peer_link")
                            if desired_use_vpl is None:
                                desired_use_vpl = desired_item.get(VpcFieldNames.USE_VIRTUAL_PEER_LINK)

                        # Narrow override: trust direct payload only for write states
                        # when it matches desired pair intent.
                        if state in ("merged", "replaced", "overridden") and desired_item is not None:
                            if desired_use_vpl is None or bool(desired_use_vpl) == bool(use_vpl):
                                nrm.module.warn(
                                    f"Overview membership check returned 'not paired' for switch {switch_id}, "
                                    "but direct /vpcPair matched requested config. Treating pair as active."
                                )
                                membership = True
                    if membership is False:
                        pending_delete.append({
                            VpcFieldNames.SWITCH_ID: switch_id,
                            VpcFieldNames.PEER_SWITCH_ID: resolved_peer_switch_id,
                            VpcFieldNames.USE_VIRTUAL_PEER_LINK: use_vpl,
                        })
                    else:
                        have.append({
                            VpcFieldNames.SWITCH_ID: switch_id,
                            VpcFieldNames.PEER_SWITCH_ID: resolved_peer_switch_id,
                            VpcFieldNames.USE_VIRTUAL_PEER_LINK: use_vpl,
                        })
                else:
                    # Direct query failed - fall back to recommendation.
                    try:
                        recommendation = _get_recommendation_details(nd_v2, fabric_name, switch_id)
                    except Exception as rec_error:
                        error_msg = str(rec_error).splitlines()[0]
                        nrm.module.warn(
                            f"Recommendation query failed for switch {switch_id}: {error_msg}. "
                            f"Unable to read configured vPC pair details."
                        )
                        recommendation = None

                    if recommendation:
                        resolved_peer_switch_id = _get_api_field_value(recommendation, "serialNumber") or peer_switch_id
                        if resolved_peer_switch_id:
                            processed_switches.add(resolved_peer_switch_id)
                        use_vpl = _get_api_field_value(recommendation, "useVirtualPeerLink", False)
                        have.append({
                            VpcFieldNames.SWITCH_ID: switch_id,
                            VpcFieldNames.PEER_SWITCH_ID: resolved_peer_switch_id,
                            VpcFieldNames.USE_VIRTUAL_PEER_LINK: use_vpl,
                        })
                    else:
                        # VPC configured but query failed - mark as pending delete.
                        pending_delete.append({
                            VpcFieldNames.SWITCH_ID: switch_id,
                            VpcFieldNames.PEER_SWITCH_ID: peer_switch_id,
                            VpcFieldNames.USE_VIRTUAL_PEER_LINK: False,
                        })
            elif not config_switch_ids or switch_id in config_switch_ids:
                # For unconfigured switches, prefer direct vPC pair query first.
                try:
                    vpc_pair_path = VpcPairEndpoints.switch_vpc_pair(fabric_name, switch_id)
                    rest_send = nd_v2._get_rest_send()
                    rest_send.save_settings()
                    rest_send.timeout = 5
                    try:
                        direct_vpc = nd_v2.request(vpc_pair_path, HttpVerbEnum.GET)
                    finally:
                        rest_send.restore_settings()
                except (NDModuleError, Exception):
                    direct_vpc = None

                if direct_vpc:
                    peer_switch_id = direct_vpc.get(VpcFieldNames.PEER_SWITCH_ID)
                    if peer_switch_id:
                        processed_switches.add(switch_id)
                        processed_switches.add(peer_switch_id)

                        use_vpl = _get_api_field_value(direct_vpc, "useVirtualPeerLink", False)
                        membership = _is_switch_in_vpc_pair(
                            nd_v2, fabric_name, switch_id, timeout=5
                        )
                        if membership is False:
                            pair_key = tuple(sorted([switch_id, peer_switch_id]))
                            desired_item = desired_pairs.get(pair_key)
                            desired_use_vpl = None
                            if desired_item:
                                desired_use_vpl = desired_item.get("use_virtual_peer_link")
                                if desired_use_vpl is None:
                                    desired_use_vpl = desired_item.get(VpcFieldNames.USE_VIRTUAL_PEER_LINK)

                            if state in ("merged", "replaced", "overridden") and desired_item is not None:
                                if desired_use_vpl is None or bool(desired_use_vpl) == bool(use_vpl):
                                    nrm.module.warn(
                                        f"Overview membership check returned 'not paired' for switch {switch_id}, "
                                        "but direct /vpcPair matched requested config. Treating pair as active."
                                    )
                                    membership = True
                        if membership is False:
                            pending_delete.append({
                                VpcFieldNames.SWITCH_ID: switch_id,
                                VpcFieldNames.PEER_SWITCH_ID: peer_switch_id,
                                VpcFieldNames.USE_VIRTUAL_PEER_LINK: use_vpl,
                            })
                        else:
                            have.append({
                                VpcFieldNames.SWITCH_ID: switch_id,
                                VpcFieldNames.PEER_SWITCH_ID: peer_switch_id,
                                VpcFieldNames.USE_VIRTUAL_PEER_LINK: use_vpl,
                            })
                else:
                    # No direct pair; check recommendation for pending create candidates.
                    try:
                        recommendation = _get_recommendation_details(nd_v2, fabric_name, switch_id)
                    except Exception as rec_error:
                        error_msg = str(rec_error).splitlines()[0]
                        nrm.module.warn(
                            f"Recommendation query failed for switch {switch_id}: {error_msg}. "
                            f"No recommendation details available."
                        )
                        recommendation = None

                    if recommendation:
                        peer_switch_id = _get_api_field_value(recommendation, "serialNumber")
                        if peer_switch_id:
                            processed_switches.add(switch_id)
                            processed_switches.add(peer_switch_id)

                            use_vpl = _get_api_field_value(recommendation, "useVirtualPeerLink", False)
                            pending_create.append({
                                VpcFieldNames.SWITCH_ID: switch_id,
                                VpcFieldNames.PEER_SWITCH_ID: peer_switch_id,
                                VpcFieldNames.USE_VIRTUAL_PEER_LINK: use_vpl,
                            })

        # Step 4: Store all states for use in create/update/delete.
        nrm.module.params["_have"] = have
        nrm.module.params["_pending_create"] = pending_create
        nrm.module.params["_pending_delete"] = pending_delete

        # Build effective existing set for state reconciliation:
        # - Include active pairs (have) and pending-create pairs.
        # - Exclude pending-delete pairs from active set to avoid stale
        #   idempotence false-negatives right after unpair operations.
        pair_by_key = {}
        for pair in pending_create + have:
            switch_id = pair.get(VpcFieldNames.SWITCH_ID)
            peer_switch_id = pair.get(VpcFieldNames.PEER_SWITCH_ID)
            if not switch_id or not peer_switch_id:
                continue
            key = tuple(sorted([switch_id, peer_switch_id]))
            pair_by_key[key] = pair

        for pair in pending_delete:
            switch_id = pair.get(VpcFieldNames.SWITCH_ID)
            peer_switch_id = pair.get(VpcFieldNames.PEER_SWITCH_ID)
            if not switch_id or not peer_switch_id:
                continue
            key = tuple(sorted([switch_id, peer_switch_id]))
            pair_by_key.pop(key, None)

        existing_pairs = list(pair_by_key.values())
        return existing_pairs

    except NDModuleError as error:
        error_dict = error.to_dict()
        if "msg" in error_dict:
            error_dict["api_error_msg"] = error_dict.pop("msg")
        _raise_vpc_error(
            msg=f"Failed to query VPC pairs: {error.msg}",
            fabric=fabric_name,
            **error_dict
        )
    except VpcPairResourceError:
        raise
    except Exception as e:
        _raise_vpc_error(
            msg=f"Failed to query VPC pairs: {str(e)}",
            fabric=fabric_name,
            exception_type=type(e).__name__
        )

