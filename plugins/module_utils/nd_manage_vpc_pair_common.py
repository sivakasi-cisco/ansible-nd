# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Sivakami S <sivakasi@cisco.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

import traceback
from typing import Any, Dict, List

from ansible_collections.cisco.nd.plugins.module_utils.endpoints.v1.manage_vpc_pair.vpc_pair_resources import (
    VpcPairResourceError,
)

# DeepDiff for intelligent change detection
try:
    from deepdiff import DeepDiff
    HAS_DEEPDIFF = True
    DEEPDIFF_IMPORT_ERROR = None
except ImportError:
    HAS_DEEPDIFF = False
    DEEPDIFF_IMPORT_ERROR = traceback.format_exc()

def _collection_to_list_flex(collection) -> List[Dict[str, Any]]:
    """
    Serialize NDConfigCollection across old/new framework variants.
    """
    if collection is None:
        return []
    if hasattr(collection, "to_list"):
        return collection.to_list()
    if hasattr(collection, "to_payload_list"):
        return collection.to_payload_list()
    if hasattr(collection, "to_ansible_config"):
        return collection.to_ansible_config()
    return []


def _raise_vpc_error(msg: str, **details: Any) -> None:
    """Raise a structured vpc_pair error for main() to format via fail_json."""
    raise VpcPairResourceError(msg=msg, **details)


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


