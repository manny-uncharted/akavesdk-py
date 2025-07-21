"""Shared, SDK-wide helper types."""

from typing import Protocol, Union
from eth_typing import HexAddress


class Signer(Protocol):
    """
    Minimal interface for *anything* that can sign and broadcast a transaction.

    A `Signer` may be an `eth_account.LocalAccount`, a custom wrapper,
    or a test double in unit‑tests – as long as it exposes the two attributes
    below.
    """
    address: HexAddress
    key: Union[str, bytes]
