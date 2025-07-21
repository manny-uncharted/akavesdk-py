"""akave_sdk.types
Domain‑specific aliases & interfaces for strong typing.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import NewType, Protocol, Union, runtime_checkable, Sequence, ByteString

# ──────────────────────────────────────────────────────────────
#   Core alias primitives
# ──────────────────────────────────────────────────────────────
# Timestamp can land as POSIX seconds, millis, or a datetime.
Timestamp = Union[int, float, datetime]

# Content Identifier (multiformats‑cid).  Fallback = str wrapper.
try:
    from multiformats.cid import CID as _CID
    CIDLike = _CID  # pragma:  no cover
except ImportError:                           # noqa:  WPS440
    CIDLike = NewType("CIDLike", str)

# 32‑byte node ID or peer ID (libp2p style) – raw or base58 string.
NodeID = Union[bytes, str]

# Nonce bytes – always 32 bytes on‑chain.
NonceBytes = bytes



# ──────────────────────────────────────────────────────────────
#   Protocol definitions (shape contracts)
# ──────────────────────────────────────────────────────────────
@runtime_checkable
class BlockUpload(Protocol):
    cid: CIDLike | str
    data: ByteString
    node_address: str
    node_id: str | bytes
    permit: bytes | str  # on‑chain permit

@runtime_checkable
class GRPCChannel(Protocol):
    def close(self) -> None: ...
    def unary_unary(self, method: str, *, request_serializer=None, response_deserializer=None): ...

# Any ctx we get from callers (FastAPI starlette.Request.state, etc.)
class CancellableContext(Protocol):
    def done(self) -> bool: ...
