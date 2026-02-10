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
Reusable mixin classes for VPC pair endpoint models.

This module provides mixin classes that can be composed to add common
fields to endpoint models without duplication.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type
__author__ = "Sivakami Sivaraman"

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from pydantic import BaseModel, Field
else:
    try:
        from pydantic import BaseModel, Field
    except ImportError:
        # Fallback for environments without pydantic
        class BaseModel:
            pass

        def Field(*args, **kwargs):
            return None


class FabricNameMixin(BaseModel):
    """Mixin for endpoints that require fabric_name parameter."""

    fabric_name: Optional[str] = Field(default=None, min_length=1, max_length=64, description="Fabric name")


class SwitchIdMixin(BaseModel):
    """Mixin for endpoints that require switch_id parameter."""

    switch_id: Optional[str] = Field(default=None, min_length=1, description="Switch serial number")


class PeerSwitchIdMixin(BaseModel):
    """Mixin for endpoints that require peer_switch_id parameter."""

    peer_switch_id: Optional[str] = Field(default=None, min_length=1, description="Peer switch serial number")


class UseVirtualPeerLinkMixin(BaseModel):
    """Mixin for endpoints that require use_virtual_peer_link parameter."""

    use_virtual_peer_link: Optional[bool] = Field(default=False, description="Indicates whether a virtual peer link is present")


class FromClusterMixin(BaseModel):
    """Mixin for endpoints that support fromCluster query parameter."""

    from_cluster: Optional[str] = Field(default=None, description="Optional cluster name")


class TicketIdMixin(BaseModel):
    """Mixin for endpoints that support ticketId query parameter."""

    ticket_id: Optional[str] = Field(default=None, description="Change ticket ID")


class ComponentTypeMixin(BaseModel):
    """Mixin for endpoints that require componentType query parameter."""

    component_type: Optional[str] = Field(default=None, description="Component type for filtering response")


class FilterMixin(BaseModel):
    """Mixin for endpoints that support filter query parameter."""

    filter: Optional[str] = Field(default=None, description="Filter expression for results")


class PaginationMixin(BaseModel):
    """Mixin for endpoints that support pagination parameters."""

    max: Optional[int] = Field(default=None, ge=1, description="Maximum number of results")
    offset: Optional[int] = Field(default=None, ge=0, description="Offset for pagination")


class SortMixin(BaseModel):
    """Mixin for endpoints that support sort parameter."""

    sort: Optional[str] = Field(default=None, description="Sort field and direction (e.g., 'name:asc')")


class ViewMixin(BaseModel):
    """Mixin for endpoints that support view parameter."""

    view: Optional[str] = Field(default=None, description="Optional view type for filtering results")
