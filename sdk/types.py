# akavesdk/types.py
from __future__ import annotations
from datetime import datetime
from typing import NewType, Union


# Type for timestamp fields that could be different formats
"""
Upstream protobuf stubs expose google.protobuf.Timestamp,
gRPC responses often arrive as epoch ints/floats,
and we sometimes coerce them to `datetime`.
"""
TimestampType = Union[datetime, float, int]


# ────────────────────────────────
#   C I D   /   M H
# ────────────────────────────────

"""
Content Identifier (multiformats-cid). Fallback = str wrapper.
"""
try:
    from multiformats.cid import CID as _CID # type: ignore
    CID = _CID
except ImportError:
    CID = NewType("CID", str) # pragma: no cover
