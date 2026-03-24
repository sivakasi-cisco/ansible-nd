# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Sivakami Sivaraman <sivakasi@cisco.com>

# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, List, Literal, Tuple, Union, Annotated
from ansible_collections.cisco.nd.plugins.module_utils.common.pydantic_compat import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
)
from ansible_collections.cisco.nd.plugins.module_utils.utils import issubset
from typing_extensions import Self


def coerce_str_to_int(data):
    """
    Convert string to int, handle None.

    Args:
        data: Value to coerce (str, int, or None)

    Returns:
        Integer value, or None if input is None.

    Raises:
        ValueError: If string cannot be converted to int
    """
    if data is None:
        return None
    if isinstance(data, str):
        if data.strip() and data.lstrip("-").isdigit():
            return int(data)
        raise ValueError(f"Cannot convert '{data}' to int")
    return int(data)


def coerce_to_bool(data):
    """
    Convert various formats to bool.

    Args:
        data: Value to coerce (str, bool, int, or None)

    Returns:
        Boolean value, or None if input is None.
        Strings 'true', '1', 'yes', 'on' map to True.
    """
    if data is None:
        return None
    if isinstance(data, str):
        return data.lower() in ("true", "1", "yes", "on")
    return bool(data)


def coerce_list_of_str(data):
    """
    Ensure data is a list of strings.

    Args:
        data: Value to coerce (str, list, or None)

    Returns:
        List of strings, or None if input is None.
        Comma-separated strings are split into list items.
    """
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


class NDVpcPairBaseModel(BaseModel, ABC):
    """
    Base model for VPC pair objects with identifiers.

    Similar to NDBaseModel from base.py but specific to VPC pair resources.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        validate_assignment=True,
        populate_by_name=True,
        extra="ignore",
    )

    identifiers: ClassVar[List[str]] = []
    identifier_strategy: ClassVar[Literal["single", "composite", "hierarchical"]] = "composite"
    exclude_from_diff: ClassVar[List[str]] = []

    @abstractmethod
    def to_payload(self) -> Dict[str, Any]:
        """
        Convert model to API payload format.

        Returns:
            Dict with camelCase API field names.
        """
        pass

    @classmethod
    @abstractmethod
    def from_response(cls, response: Dict[str, Any]) -> Self:
        """
        Create model instance from API response.

        Args:
            response: Dict from ND API response

        Returns:
            Validated model instance.
        """
        pass

    def get_identifier_value(self) -> Union[str, int, Tuple[Any, ...]]:
        """
        Extract identifier value(s) from this instance.

        Uses the configured identifier_strategy (single, composite, or hierarchical)
        to determine how to extract and return the identifier.

        Returns:
            Single value for 'single' strategy, tuple for 'composite',
            or (field_name, value) tuple for 'hierarchical'.

        Raises:
            ValueError: If identifiers are not defined, required fields are None,
                or strategy is unknown.
        """
        if not self.identifiers:
            raise ValueError(f"{self.__class__.__name__} has no identifiers defined")

        if self.identifier_strategy == "single":
            value = getattr(self, self.identifiers[0], None)
            if value is None:
                raise ValueError(f"Single identifier field '{self.identifiers[0]}' is None")
            return value

        if self.identifier_strategy == "composite":
            values = []
            missing = []

            for field in self.identifiers:
                value = getattr(self, field, None)
                if value is None:
                    missing.append(field)
                values.append(value)

            if missing:
                raise ValueError(
                    f"Composite identifier fields {missing} are None. All required: {self.identifiers}"
                )

            return tuple(values)

        if self.identifier_strategy == "hierarchical":
            for field in self.identifiers:
                value = getattr(self, field, None)
                if value is not None:
                    return (field, value)

            raise ValueError(f"No non-None value in hierarchical fields {self.identifiers}")

        raise ValueError(f"Unknown identifier strategy: {self.identifier_strategy}")

    def get_switch_pair_key(self) -> str:
        """
        Generate a unique key for VPC pair (sorted switch IDs).

        Returns:
            Deterministic "ID1-ID2" string with sorted switch serial numbers.

        Raises:
            ValueError: If identifier_strategy is not composite with 2 identifiers
        """
        if self.identifier_strategy != "composite" or len(self.identifiers) != 2:
            raise ValueError(
                "get_switch_pair_key only works with composite strategy and 2 identifiers"
            )

        values = self.get_identifier_value()
        sorted_ids = sorted([str(v) for v in values])
        return f"{sorted_ids[0]}-{sorted_ids[1]}"

    def to_diff_dict(self) -> Dict[str, Any]:
        """
        Export for diff comparison (excludes sensitive fields).

        Returns:
            Dict with alias keys, excluding None and exclude_from_diff fields.
        """
        return self.model_dump(
            by_alias=True,
            exclude_none=True,
            exclude=set(self.exclude_from_diff),
        )

    def get_diff(self, other: "NDVpcPairBaseModel") -> bool:
        """
        Return True when ``other`` is a subset of this model for diff checks.

        Args:
            other: Model instance to compare against

        Returns:
            True if other's diff dict is a subset of self's diff dict.
        """
        self_data = self.to_diff_dict()
        other_data = other.to_diff_dict()
        return issubset(other_data, self_data)

    def merge(self, other: "NDVpcPairBaseModel") -> "NDVpcPairBaseModel":
        """
        Merge another model's non-None values into this model instance.

        Nested NDVpcPairBaseModel values are merged recursively.

        Args:
            other: Model instance whose non-None fields overwrite this model

        Returns:
            Self with merged values.

        Raises:
            TypeError: If other is not the same type as self
        """
        if not isinstance(other, type(self)):
            raise TypeError(
                f"Cannot merge {type(other).__name__} into {type(self).__name__}. "
                "Both must be the same type."
            )

        for field_name, value in other:
            if value is None:
                continue

            current = getattr(self, field_name, None)
            if isinstance(current, NDVpcPairBaseModel) and isinstance(value, NDVpcPairBaseModel):
                current.merge(value)
            else:
                setattr(self, field_name, value)

        return self
