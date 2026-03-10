# -*- coding: utf-8 -*-

# Copyright: (c) 2025, Sivakami Sivaraman <sivakasi@cisco.com>

# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
Backward-compatible export surface for vPC pair playbook models.

The implementation is split following the PR172 style:
- base.py: coercion helpers and base model
- nested.py: nested-model base class
- vpc_pair_models.py: vPC-pair-specific schemas
"""

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
