from __future__ import annotations

import struct
from typing import Final, Iterable, Mapping, Sequence, Union

from Crypto.Hash import keccak
from eth_keys import keys
from eth_utils import to_checksum_address  # noqa: F401  – kept for external users


_json_val = Union[str, int, bytes, bytearray, bool, "CID"]  # recursive not needed here
JsonMapping = Mapping[str, _json_val]


class TypedData:
    __slots__ = ("name", "type")

    def __init__(self, name: str, type_name: str) -> None:
        self.name = name
        self.type = type_name


class Domain:
    __slots__ = ("name", "version", "chain_id", "verifying_contract")

    def __init__(self, name: str, version: str, chain_id: int, verifying_contract: str) -> None:
        self.name = name
        self.version = version
        self.chain_id = chain_id
        self.verifying_contract = verifying_contract


def sign(
    private_key_bytes: bytes,
    domain: Domain,
    data_message: JsonMapping,
    data_types: Mapping[str, Sequence[TypedData]],
) -> bytes:
    """Return the raw *65-byte* ``r || s || v`` signature."""
    hash_bytes = _hash_typed_data(domain, data_message, data_types)

    pk = keys.PrivateKey(private_key_bytes)
    sig = pk.sign_msg_hash(hash_bytes).to_bytes()
    sig_array = bytearray(sig)
    sig_array[64] += 27  # make v ∈ {27,28}
    return bytes(sig_array)


def _encode_type(primary_type: str, types: Mapping[str, Sequence[TypedData]]) -> str:
    fields = ",".join(f"{f.type} {f.name}" for f in types[primary_type])
    return f"{primary_type}({fields})"


def _type_hash(primary_type: str, types: Mapping[str, Sequence[TypedData]]) -> bytes:
    encoded_type = _encode_type(primary_type, types)
    return keccak.new(digest_bits=256, data=encoded_type.encode()).digest()


def _hash_typed_data(
    domain: Domain,
    data_message: JsonMapping,
    data_types: Mapping[str, Sequence[TypedData]],
) -> bytes:
    domain_types: Mapping[str, Sequence[TypedData]] = {
        "EIP712Domain": (
            TypedData("name", "string"),
            TypedData("version", "string"),
            TypedData("chainId", "uint256"),
            TypedData("verifyingContract", "address"),
        )
    }

    domain_msg: JsonMapping = {
        "name": domain.name,
        "version": domain.version,
        "chainId": domain.chain_id,
        "verifyingContract": domain.verifying_contract,
    }

    domain_hash = _encode_data("EIP712Domain", domain_msg, domain_types)
    data_hash = _encode_data("StorageData", data_message, data_types)

    raw = bytes([0x19, 0x01]) + domain_hash + data_hash
    return keccak.new(digest_bits=256, data=raw).digest()


def _encode_data(
    primary_type: str,
    data: JsonMapping,
    types: Mapping[str, Sequence[TypedData]],
) -> bytes:
    type_hash_bytes = _type_hash(primary_type, types)
    encoded: list[bytes] = [type_hash_bytes] + [
        _encode_value(data[f.name], f.type) for f in types[primary_type]
    ]
    return keccak.new(digest_bits=256, data=b"".join(encoded)).digest()


def _encode_value(value: _json_val, type_name: str) -> bytes:
    # (body identical to your original, just renamed internals)
    if type_name == "string":
        if not isinstance(value, str):
            raise TypeError("expected string")
        return keccak.new(digest_bits=256, data=value.encode()).digest()

    if type_name == "bytes":
        if not isinstance(value, (bytes, bytearray)):
            raise TypeError("expected bytes")
        return keccak.new(digest_bits=256, data=value).digest()

    if type_name == "bytes32":
        if not isinstance(value, (bytes, bytearray)) or len(value) != 32:
            raise TypeError("bytes32 must be exactly 32 bytes")
        return bytes(value)

    if type_name == "uint8":
        if not isinstance(value, int) or not (0 <= value <= 255):
            raise ValueError("uint8 out of range")
        return (b"\x00" * 31) + bytes([value])

    if type_name == "uint64":
        if not isinstance(value, int) or not (0 <= value < 1 << 64):
            raise ValueError("uint64 out of range")
        buf = bytearray(32)
        struct.pack_into(">Q", buf, 24, value)
        return bytes(buf)

    if type_name == "uint256":
        if not isinstance(value, int) or value < 0:
            raise ValueError("uint256 must be non‑negative int")
        return value.to_bytes(32, "big")

    if type_name == "address":
        if isinstance(value, str):
            v = bytes.fromhex(value[2:] if value.startswith("0x") else value)
        elif isinstance(value, (bytes, bytearray)):
            v = bytes(value)
        else:
            raise TypeError("address must be str/bytes")
        if len(v) != 20:
            raise ValueError("address length must be 20 bytes")
        return b"\x00" * 12 + v

    raise ValueError(f"unsupported type: {type_name}")


def recover_signer_address(
    signature: bytes,
    domain: Domain,
    data_message: JsonMapping,
    data_types: Mapping[str, Sequence[TypedData]],
) -> str:
    """
    Recover the **checksum‑formatted** Ethereum address that produced *signature*.

    :param signature: 65-byte ``r || s || v`` where ``v ∈ {27,28}``.
    :param domain: The same values that were given to :func:`sign`.
    :param data_message: The same values that were given to :func:`sign`.
    :param data_types: The same values that were given to :func:`sign`.

    :returns: The recovered address (EIP-55 checksum encoded).

    :raises ValueError: If the signature has an invalid length or *v* byte.
    """
    if len(signature) != 65:
        raise ValueError("EIP-712 signature must be exactly 65 bytes")

    sig_array = bytearray(signature)
    if sig_array[64] not in (27, 28):
        raise ValueError("signature v-byte must be 27 or 28")
    sig_array[64] -= 27  # convert back to {0,1} for eth_keys

    hash_bytes = _hash_typed_data(domain, data_message, data_types)

    from eth_keys import keys  # local import to avoid heavy dep at module import
    sig_obj = keys.Signature(bytes(sig_array))
    pub_key = sig_obj.recover_public_key_from_msg_hash(hash_bytes)
    return pub_key.to_checksum_address()