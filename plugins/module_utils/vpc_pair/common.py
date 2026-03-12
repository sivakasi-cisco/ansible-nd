# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Sivakami S <sivakasi@cisco.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

from typing import Any


def build_path(base: str, *segments: str) -> str:
    """Build a path from a base and optional path segments."""
    if not segments:
        return base
    return f"{base}/{'/'.join(segments)}"


def require_non_empty_str(name: str, value: Any, owner: str) -> str:
    """Validate a required non-empty string parameter and return its stripped value."""
    if not value or not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"{owner}: {name} must be a non-empty string. "
            f"Got: {value!r} (type: {type(value).__name__})"
        )
    return value.strip()
