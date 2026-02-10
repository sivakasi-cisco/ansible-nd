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
Enums for VPC pair management.

This module provides enumeration types used throughout the VPC pair
management implementation.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type
__author__ = "Sivakami Sivaraman"

from enum import Enum


class VerbEnum(str, Enum):
    """
    # Summary

    Enum for HTTP verb values used in endpoints.

    ## Members

    - GET: Represents the HTTP GET method.
    - POST: Represents the HTTP POST method.
    - PUT: Represents the HTTP PUT method.
    - DELETE: Represents the HTTP DELETE method.
    """

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class VpcActionEnum(str, Enum):
    """
    # Summary

    Enum for VPC pair action types.

    ## Members

    - PAIR: Action to create/pair a VPC.
    - UNPAIR: Action to delete/unpair a VPC.
    """

    PAIR = "pair"
    UNPAIR = "unPair"


class VpcPairTypeEnum(str, Enum):
    """
    # Summary

    Enum for VPC pair template types.

    ## Members

    - DEFAULT: Uses default VPC pair template.
    - CUSTOM: Uses custom VPC pair template.
    """

    DEFAULT = "default"
    CUSTOM = "custom"


class KeepAliveVrfEnum(str, Enum):
    """
    # Summary

    Enum for VPC keep-alive VRF options.

    ## Members

    - DEFAULT: Use default VRF for keep-alive.
    - MANAGEMENT: Use management VRF for keep-alive.
    """

    DEFAULT = "default"
    MANAGEMENT = "management"


class PoModeEnum(str, Enum):
    """
    # Summary

    Enum for port-channel mode options.

    ## Members

    - ON: Static channel mode (no protocol).
    - ACTIVE: LACP active mode.
    - PASSIVE: LACP passive mode.
    """

    ON = "on"
    ACTIVE = "active"
    PASSIVE = "passive"


class ComponentTypeOverviewEnum(str, Enum):
    """
    # Summary

    Enum for VPC pair overview component types.

    ## Members

    - FULL: Full overview with all components.
    - HEALTH: Health status only.
    - MODULE: Module information only.
    - VXLAN: VXLAN configuration only.
    - OVERLAY: Overlay information only.
    - PAIRS_INFO: Pairs information only.
    - INVENTORY: Inventory information only.
    - ANOMALIES: Anomalies information only.
    """

    FULL = "full"
    HEALTH = "health"
    MODULE = "module"
    VXLAN = "vxlan"
    OVERLAY = "overlay"
    PAIRS_INFO = "pairsInfo"
    INVENTORY = "inventory"
    ANOMALIES = "anomalies"


class ComponentTypeSupportEnum(str, Enum):
    """
    # Summary

    Enum for VPC pair support check types.

    ## Members

    - CHECK_PAIRING: Check if pairing is allowed.
    - CHECK_FABRIC_PEERING_SUPPORT: Check fabric peering support.
    """

    CHECK_PAIRING = "checkPairing"
    CHECK_FABRIC_PEERING_SUPPORT = "checkFabricPeeringSupport"


class VpcPairViewEnum(str, Enum):
    """
    # Summary

    Enum for VPC pairs list view options.

    ## Members

    - INTENDED_PAIRS: Show intended VPC pairs.
    - DISCOVERED_PAIRS: Show discovered VPC pairs (default).
    """

    INTENDED_PAIRS = "intendedPairs"
    DISCOVERED_PAIRS = "discoveredPairs"


class PortChannelDuplexEnum(str, Enum):
    """
    # Summary

    Enum for port-channel duplex options.

    ## Members

    - HALF: Half duplex mode.
    - FULL: Full duplex mode.
    """

    HALF = "half"
    FULL = "full"


class MaintenanceModeEnum(str, Enum):
    """
    # Summary

    Enum for switch maintenance mode.

    ## Members

    - MAINTENANCE: Switch is in maintenance mode.
    - NORMAL: Switch is in normal operation mode.
    """

    MAINTENANCE = "maintenance"
    NORMAL = "normal"


class VpcRoleEnum(str, Enum):
    """
    # Summary

    Enum for VPC role designation.

    ## Members

    - PRIMARY: Primary VPC peer.
    - SECONDARY: Secondary VPC peer.
    """

    PRIMARY = "primary"
    SECONDARY = "secondary"
