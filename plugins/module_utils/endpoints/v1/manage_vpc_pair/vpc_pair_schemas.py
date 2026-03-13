# -*- coding: utf-8 -*-

# Copyright: (c) 2025, Sivakami Sivaraman <sivakasi@cisco.com>

# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

"""
Backward-compatible export surface for vPC pair schemas.

Primary source of truth lives in `plugins/models/vpc_pair_models.py`.
This module also provides local fallback models for AnsiballZ runtimes where
`plugins/models` files may not be packaged.
"""

from typing import Any, Dict, List, Optional, Literal, Annotated

from ansible_collections.cisco.nd.plugins.module_utils.common.pydantic_compat import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
)

try:
    from ansible_collections.cisco.nd.plugins.models.base import (  # noqa: F401
        coerce_str_to_int,
        coerce_to_bool,
        coerce_list_of_str,
        FlexibleInt,
        FlexibleBool,
        FlexibleListStr,
        NDVpcPairBaseModel,
    )
    from ansible_collections.cisco.nd.plugins.models.nested import NDVpcPairNestedModel  # noqa: F401
    from ansible_collections.cisco.nd.plugins.models.vpc_pair_models import *  # noqa: F401,F403
except Exception:
    from ansible_collections.cisco.nd.plugins.module_utils.endpoints.v1.manage_vpc_pair.enums import (  # noqa: F401
        KeepAliveVrfEnum,
    )

    def coerce_str_to_int(data):
        if data is None:
            return None
        if isinstance(data, str):
            if data.strip() and data.lstrip("-").isdigit():
                return int(data)
            raise ValueError(f"Cannot convert '{data}' to int")
        return int(data)

    def coerce_to_bool(data):
        if data is None:
            return None
        if isinstance(data, str):
            return data.lower() in ("true", "1", "yes", "on")
        return bool(data)

    def coerce_list_of_str(data):
        if data is None:
            return None
        if isinstance(data, str):
            return [item.strip() for item in data.split(",") if item.strip()]
        if isinstance(data, list):
            return [str(item) for item in data]
        return data

    FlexibleInt = Annotated[int, BeforeValidator(coerce_str_to_int)]
    FlexibleBool = Annotated[bool, BeforeValidator(coerce_to_bool)]
    FlexibleListStr = Annotated[List[str], BeforeValidator(coerce_list_of_str)]

    class _VpcPairDetailsBaseModel(BaseModel):
        model_config = ConfigDict(
            str_strip_whitespace=True,
            use_enum_values=True,
            validate_assignment=True,
            populate_by_name=True,
            extra="ignore",
        )

    class VpcPairDetailsDefault(_VpcPairDetailsBaseModel):
        """Default template vPC pair configuration."""

        type: Literal["default"] = Field(default="default", alias="type", description="Template type")
        domain_id: Optional[FlexibleInt] = Field(default=None, alias="domainId", description="VPC domain ID")
        switch_keep_alive_local_ip: Optional[str] = Field(default=None, alias="switchKeepAliveLocalIp", description="Peer-1 keep-alive IP")
        peer_switch_keep_alive_local_ip: Optional[str] = Field(default=None, alias="peerSwitchKeepAliveLocalIp", description="Peer-2 keep-alive IP")
        keep_alive_vrf: Optional[KeepAliveVrfEnum] = Field(default=None, alias="keepAliveVrf", description="Keep-alive VRF")
        keep_alive_hold_timeout: Optional[FlexibleInt] = Field(default=3, alias="keepAliveHoldTimeout", description="Keep-alive hold timeout")
        enable_mirror_config: Optional[FlexibleBool] = Field(default=False, alias="enableMirrorConfig", description="Enable config mirroring")
        is_vpc_plus: Optional[FlexibleBool] = Field(default=False, alias="isVpcPlus", description="VPC+ topology")
        fabric_path_switch_id: Optional[FlexibleInt] = Field(default=None, alias="fabricPathSwitchId", description="FabricPath switch ID")
        is_vteps: Optional[FlexibleBool] = Field(default=False, alias="isVteps", description="Configure NVE source loopback")
        nve_interface: Optional[FlexibleInt] = Field(default=1, alias="nveInterface", description="NVE interface")
        switch_source_loopback: Optional[FlexibleInt] = Field(default=None, alias="switchSourceLoopback", description="Peer-1 source loopback")
        peer_switch_source_loopback: Optional[FlexibleInt] = Field(default=None, alias="peerSwitchSourceLoopback", description="Peer-2 source loopback")
        switch_primary_ip: Optional[str] = Field(default=None, alias="switchPrimaryIp", description="Peer-1 primary IP")
        peer_switch_primary_ip: Optional[str] = Field(default=None, alias="peerSwitchPrimaryIp", description="Peer-2 primary IP")
        loopback_secondary_ip: Optional[str] = Field(default=None, alias="loopbackSecondaryIp", description="Secondary loopback IP")
        switch_domain_config: Optional[str] = Field(default=None, alias="switchDomainConfig", description="Peer-1 domain config CLI")
        peer_switch_domain_config: Optional[str] = Field(default=None, alias="peerSwitchDomainConfig", description="Peer-2 domain config CLI")
        switch_po_id: Optional[FlexibleInt] = Field(default=None, alias="switchPoId", description="Peer-1 port-channel ID")
        peer_switch_po_id: Optional[FlexibleInt] = Field(default=None, alias="peerSwitchPoId", description="Peer-2 port-channel ID")
        switch_member_interfaces: Optional[FlexibleListStr] = Field(default=None, alias="switchMemberInterfaces", description="Peer-1 member interfaces")
        peer_switch_member_interfaces: Optional[FlexibleListStr] = Field(default=None, alias="peerSwitchMemberInterfaces", description="Peer-2 member interfaces")
        po_mode: Optional[str] = Field(default="active", alias="poMode", description="Port-channel mode")
        switch_po_description: Optional[str] = Field(default=None, alias="switchPoDescription", description="Peer-1 port-channel description")
        peer_switch_po_description: Optional[str] = Field(default=None, alias="peerSwitchPoDescription", description="Peer-2 port-channel description")
        admin_state: Optional[FlexibleBool] = Field(default=True, alias="adminState", description="Admin state")
        allowed_vlans: Optional[str] = Field(default="all", alias="allowedVlans", description="Allowed VLANs")
        switch_native_vlan: Optional[FlexibleInt] = Field(default=None, alias="switchNativeVlan", description="Peer-1 native VLAN")
        peer_switch_native_vlan: Optional[FlexibleInt] = Field(default=None, alias="peerSwitchNativeVlan", description="Peer-2 native VLAN")
        switch_po_config: Optional[str] = Field(default=None, alias="switchPoConfig", description="Peer-1 port-channel freeform config")
        peer_switch_po_config: Optional[str] = Field(default=None, alias="peerSwitchPoConfig", description="Peer-2 port-channel freeform config")
        fabric_name: Optional[str] = Field(default=None, alias="fabricName", description="Fabric name")

    class VpcPairDetailsCustom(_VpcPairDetailsBaseModel):
        """Custom template vPC pair configuration."""

        type: Literal["custom"] = Field(default="custom", alias="type", description="Template type")
        template_name: str = Field(alias="templateName", description="Name of the custom template")
        template_config: Dict[str, Any] = Field(alias="templateConfig", description="Free-form configuration")
