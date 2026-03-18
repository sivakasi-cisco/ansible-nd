# -*- coding: utf-8 -*-
#
# Copyright: (c) 2026, Sivakami S <sivakasi@cisco.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

from typing import Any, ClassVar, Dict, List, Literal, Optional, Union

try:
    from ansible_collections.cisco.nd.plugins.module_utils.models.manage_vpc_pair.base import (
        NDVpcPairBaseModel as _VpcPairBaseModel,
    )
except ImportError:
    from ansible_collections.cisco.nd.plugins.module_utils.common.pydantic_compat import (
        BaseModel as _VpcPairBaseModel,
    )

from ansible_collections.cisco.nd.plugins.module_utils.common.pydantic_compat import (
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from ansible_collections.cisco.nd.plugins.module_utils.endpoints.v1.manage_vpc_pair.enums import (
    VpcFieldNames,
)

try:
    from ansible_collections.cisco.nd.plugins.module_utils.models.manage_vpc_pair.vpc_pair_models import (
        VpcPairDetailsDefault,
        VpcPairDetailsCustom,
    )
except ImportError:
    from ansible_collections.cisco.nd.plugins.module_utils.endpoints.v1.manage_vpc_pair.vpc_pair_schemas import (
        VpcPairDetailsDefault,
        VpcPairDetailsCustom,
    )


class VpcPairModel(_VpcPairBaseModel):
    """
    Pydantic model for nd_manage_vpc_pair input.

    Uses a composite identifier `(switch_id, peer_switch_id)` and module-oriented
    defaults/validation behavior.
    """

    identifiers: ClassVar[List[str]] = ["switch_id", "peer_switch_id"]
    identifier_strategy: ClassVar[Literal["composite"]] = "composite"
    exclude_from_diff: ClassVar[List[str]] = []

    model_config = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        validate_assignment=True,
        populate_by_name=True,
        validate_by_alias=True,
        validate_by_name=True,
        extra="ignore",
    )

    switch_id: str = Field(
        alias=VpcFieldNames.SWITCH_ID,
        description="Peer-1 switch serial number",
        min_length=3,
        max_length=64,
    )
    peer_switch_id: str = Field(
        alias=VpcFieldNames.PEER_SWITCH_ID,
        description="Peer-2 switch serial number",
        min_length=3,
        max_length=64,
    )
    use_virtual_peer_link: bool = Field(
        default=True,
        alias=VpcFieldNames.USE_VIRTUAL_PEER_LINK,
        description="Virtual peer link enabled",
    )
    vpc_pair_details: Optional[Union[VpcPairDetailsDefault, VpcPairDetailsCustom]] = Field(
        default=None,
        discriminator="type",
        alias=VpcFieldNames.VPC_PAIR_DETAILS,
        description="VPC pair configuration details (default or custom template)",
    )

    @field_validator("switch_id", "peer_switch_id")
    @classmethod
    def validate_switch_id_format(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Switch ID cannot be empty or whitespace")
        return v.strip()

    @model_validator(mode="after")
    def validate_different_switches(self) -> "VpcPairModel":
        if self.switch_id == self.peer_switch_id:
            raise ValueError(
                f"switch_id and peer_switch_id must be different: {self.switch_id}"
            )
        return self

    def to_payload(self) -> Dict[str, Any]:
        return self.model_dump(by_alias=True, exclude_none=True)

    def to_diff_dict(self) -> Dict[str, Any]:
        return self.model_dump(
            by_alias=True,
            exclude_none=True,
            exclude=set(self.exclude_from_diff),
        )

    def get_identifier_value(self):
        return tuple(sorted([self.switch_id, self.peer_switch_id]))

    def to_config(self, **kwargs) -> Dict[str, Any]:
        return self.model_dump(by_alias=False, exclude_none=True, **kwargs)

    @classmethod
    def from_config(cls, ansible_config: Dict[str, Any]) -> "VpcPairModel":
        data = dict(ansible_config or {})

        # Accept both snake_case module input and API camelCase aliases.
        if VpcFieldNames.SWITCH_ID not in data and "switch_id" in data:
            data[VpcFieldNames.SWITCH_ID] = data.get("switch_id")
        if VpcFieldNames.PEER_SWITCH_ID not in data and "peer_switch_id" in data:
            data[VpcFieldNames.PEER_SWITCH_ID] = data.get("peer_switch_id")
        if (
            VpcFieldNames.USE_VIRTUAL_PEER_LINK not in data
            and "use_virtual_peer_link" in data
        ):
            data[VpcFieldNames.USE_VIRTUAL_PEER_LINK] = data.get("use_virtual_peer_link")
        if VpcFieldNames.VPC_PAIR_DETAILS not in data and "vpc_pair_details" in data:
            data[VpcFieldNames.VPC_PAIR_DETAILS] = data.get("vpc_pair_details")

        return cls.model_validate(data, by_alias=True, by_name=True)

    def merge(self, other_model: "VpcPairModel") -> "VpcPairModel":
        if not isinstance(other_model, type(self)):
            raise TypeError(
                "VpcPairModel.merge requires both models to be the same type"
            )

        for field, value in other_model:
            if value is None:
                continue
            setattr(self, field, value)
        return self

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> "VpcPairModel":
        data = {
            VpcFieldNames.SWITCH_ID: response.get(VpcFieldNames.SWITCH_ID),
            VpcFieldNames.PEER_SWITCH_ID: response.get(VpcFieldNames.PEER_SWITCH_ID),
            VpcFieldNames.USE_VIRTUAL_PEER_LINK: response.get(
                VpcFieldNames.USE_VIRTUAL_PEER_LINK, True
            ),
        }
        return cls.model_validate(data)
