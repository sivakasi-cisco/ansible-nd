# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Sivakami Sivaraman <sivakasi@cisco.com>

# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from typing import Any, Dict, List, ClassVar
from typing_extensions import Self
from ansible_collections.cisco.nd.plugins.models.base import NDVpcPairBaseModel


class NDVpcPairNestedModel(NDVpcPairBaseModel):
    """
    Base for nested VPC pair models without identifiers.

    Similar to NDNestedModel from PR172 split pattern.
    """

    identifiers: ClassVar[List[str]] = []

    def to_payload(self) -> Dict[str, Any]:
        """Convert model to API payload format."""
        return self.model_dump(by_alias=True, exclude_none=True)

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> Self:
        """Create model instance from API response."""
        return cls.model_validate(response)
