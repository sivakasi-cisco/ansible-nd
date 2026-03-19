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
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from ansible_collections.cisco.nd.plugins.module_utils.manage_vpc_pair.enums import (
    VpcFieldNames,
)

from ansible_collections.cisco.nd.plugins.module_utils.models.manage_vpc_pair.vpc_pair_models import (
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

    @classmethod
    def get_argument_spec(cls) -> Dict[str, Any]:
        """
        Return Ansible argument_spec for nd_manage_vpc_pair.

        Backward-compatible wrapper around the dedicated playbook config model.
        """
        return VpcPairPlaybookConfigModel.get_argument_spec()


class VpcPairPlaybookItemModel(BaseModel):
    """
    One item under playbook `config` for nd_manage_vpc_pair.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        validate_assignment=True,
        populate_by_name=True,
        validate_by_alias=True,
        validate_by_name=True,
        extra="ignore",
    )

    peer1_switch_id: str = Field(
        alias="switch_id",
        description="Peer-1 switch serial number",
        min_length=3,
        max_length=64,
    )
    peer2_switch_id: str = Field(
        alias="peer_switch_id",
        description="Peer-2 switch serial number",
        min_length=3,
        max_length=64,
    )
    use_virtual_peer_link: bool = Field(
        default=True,
        description="Virtual peer link enabled",
    )
    vpc_pair_details: Optional[Union[VpcPairDetailsDefault, VpcPairDetailsCustom]] = Field(
        default=None,
        discriminator="type",
        alias=VpcFieldNames.VPC_PAIR_DETAILS,
        description="VPC pair configuration details (default or custom template)",
    )

    @field_validator("peer1_switch_id", "peer2_switch_id")
    @classmethod
    def validate_switch_id_format(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Switch ID cannot be empty or whitespace")
        return v.strip()

    @model_validator(mode="after")
    def validate_different_switches(self) -> "VpcPairPlaybookItemModel":
        if self.peer1_switch_id == self.peer2_switch_id:
            raise ValueError(
                "peer1_switch_id and peer2_switch_id must be different: "
                f"{self.peer1_switch_id}"
            )
        return self

    def to_runtime_config(self) -> Dict[str, Any]:
        """
        Normalize playbook keys into runtime keys consumed by state machine code.
        """
        switch_id = self.peer1_switch_id
        peer_switch_id = self.peer2_switch_id
        use_virtual_peer_link = self.use_virtual_peer_link
        vpc_pair_details = self.vpc_pair_details
        return {
            "switch_id": switch_id,
            "peer_switch_id": peer_switch_id,
            "use_virtual_peer_link": use_virtual_peer_link,
            "vpc_pair_details": (
                vpc_pair_details.model_dump(by_alias=True, exclude_none=True)
                if vpc_pair_details is not None
                else None
            ),
            VpcFieldNames.SWITCH_ID: switch_id,
            VpcFieldNames.PEER_SWITCH_ID: peer_switch_id,
            VpcFieldNames.USE_VIRTUAL_PEER_LINK: use_virtual_peer_link,
            VpcFieldNames.VPC_PAIR_DETAILS: (
                vpc_pair_details.model_dump(by_alias=True, exclude_none=True)
                if vpc_pair_details is not None
                else None
            ),
        }


class VpcPairPlaybookConfigModel(BaseModel):
    """
    Top-level playbook configuration model for nd_manage_vpc_pair.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        validate_assignment=True,
        populate_by_name=True,
        validate_by_alias=True,
        validate_by_name=True,
        extra="ignore",
    )

    state: Literal["merged", "replaced", "deleted", "overridden", "gathered"] = Field(
        default="merged",
        description="Desired state for vPC pair configuration",
    )
    fabric_name: str = Field(description="Fabric name")
    deploy: bool = Field(default=False, description="Deploy after configuration changes")
    force: bool = Field(
        default=False,
        description="Force deletion without pre-deletion safety checks",
    )
    api_timeout: int = Field(
        default=30,
        description="API request timeout in seconds for write operations",
    )
    query_timeout: int = Field(
        default=10,
        description="API request timeout in seconds for query/recommendation operations",
    )
    refresh_after_apply: bool = Field(
        default=True,
        description="Refresh final after-state with a post-apply query",
    )
    refresh_after_timeout: Optional[int] = Field(
        default=None,
        description="Optional timeout for post-apply refresh query",
    )
    suppress_previous: bool = Field(
        default=False,
        description="Skip initial before-state query (merged state only)",
    )
    suppress_verification: bool = Field(
        default=False,
        description="Skip final after-state refresh query",
    )
    config: List[VpcPairPlaybookItemModel] = Field(
        default_factory=list,
        description="List of vPC pair configurations",
    )

    @classmethod
    def get_argument_spec(cls) -> Dict[str, Any]:
        """
        Return Ansible argument_spec for nd_manage_vpc_pair.
        """
        return dict(
            state=dict(
                type="str",
                default="merged",
                choices=["merged", "replaced", "deleted", "overridden", "gathered"],
            ),
            fabric_name=dict(type="str", required=True),
            deploy=dict(type="bool", default=False),
            force=dict(
                type="bool",
                default=False,
                description=(
                    "Force deletion without pre-deletion validation "
                    "(bypasses safety checks)"
                ),
            ),
            api_timeout=dict(
                type="int",
                default=30,
                description=(
                    "API request timeout in seconds for primary operations"
                ),
            ),
            query_timeout=dict(
                type="int",
                default=10,
                description=(
                    "API request timeout in seconds for query/recommendation "
                    "operations"
                ),
            ),
            refresh_after_apply=dict(
                type="bool",
                default=True,
                description=(
                    "Refresh final after-state by querying controller "
                    "after write operations"
                ),
            ),
            refresh_after_timeout=dict(
                type="int",
                required=False,
                description=(
                    "Optional timeout in seconds for post-apply after-state "
                    "refresh query"
                ),
            ),
            suppress_previous=dict(
                type="bool",
                default=False,
                description=(
                    "Skip initial controller query for before/diff baseline. "
                    "Supported only with state=merged."
                ),
            ),
            suppress_verification=dict(
                type="bool",
                default=False,
                description=(
                    "Skip post-apply controller query for after-state "
                    "verification (alias for refresh_after_apply=false)."
                ),
            ),
            config=dict(
                type="list",
                elements="dict",
                options=dict(
                    peer1_switch_id=dict(
                        type="str", required=True, aliases=["switch_id"]
                    ),
                    peer2_switch_id=dict(
                        type="str", required=True, aliases=["peer_switch_id"]
                    ),
                    use_virtual_peer_link=dict(type="bool", default=True),
                    vpc_pair_details=dict(type="dict"),
                ),
            ),
        )
