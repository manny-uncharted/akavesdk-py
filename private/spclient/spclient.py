from __future__ import annotations

from typing import Final, NewType

import requests
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    from multiformats.cid import CID as CIDType  # type: ignore
except ImportError:  # gracefully degrade – still type‑checked
    CIDType = NewType("CID", str)

URL = NewType("URL", str)


class SPClient:
    """Client for communication with Filecoin Storage Provider (SP)."""

    _TIMEOUT: Final[int] = 10  # seconds

    def __init__(self) -> None:
        self.session: Session = requests.Session()

        retry_cfg = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=(500, 502, 503, 504),
            allowed_methods=frozenset({"GET"}),
        )
        adapter = HTTPAdapter(max_retries=retry_cfg)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    
    def __enter__(self) -> "SPClient":  # noqa: DunderEnter
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: D401,DunderExit
        self.close()

    def close(self) -> None:
        """Closes the HTTP session."""
        self.session.close()

    def fetch_block(
        self,
        sp_base_url: URL,
        cid_str: CIDType,
        *,
        timeout: int | float | None = None,
    ) -> bytes:
        """
        Fetches a block from the Filecoin provider.

        :param sp_base_url: Base URL of the storage provider.
        :param cid_str: Content Identifier (CID) of the block.
        :return: Raw block data.
        :raises: Exception if the request fails or block retrieval fails.
        """
        url = f"{sp_base_url}/ipfs/{cid_str}?format=raw"
        try:
            resp = self.session.get(url, timeout=timeout or self._TIMEOUT)
            resp.raise_for_status()
            return resp.content
        except requests.RequestException as exc:  # pragma: no cover
            raise Exception(f"Failed to fetch block '{cid_str}': {exc}") from exc


# Example usage:
if __name__ == "__main__":
    sp_client = SPClient()
    try:
        block_cid = "bafybeihdwdcefgh4dqkjv67uzcmw7ojee6xedzdetojuzjevtenxquvyku"  # Example CID
        base_url = "https://filecoin-provider.com"
        block_data = sp_client.fetch_block(base_url, block_cid, timeout=30.0)
        print(f"Fetched block ({block_cid}): {block_data[:50]}...")  # Print first 50 bytes
    finally:
        sp_client.close()
