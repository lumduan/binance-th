"""Opt-in live user-data smoke test (M6).

Triple-gated: the ``integration`` marker, ``BINANCE_TH_LIVE=1``, and a real
``BINANCE_TH_API_KEY`` (listenKey is API-key-only — no secret needed). Run locally with::

    BINANCE_TH_LIVE=1 uv run pytest -m integration -k userdata_smoke

**Read-only w.r.t. trading**: it creates/keepalives/DELETEs a listenKey and connects the
user-data socket; it never places an order. Never runs in CI (the env-var gates are the
real guard).
"""

import asyncio
import os

import pytest

from binance_th import BinanceThClient
from binance_th.config import BinanceThConfig
from binance_th.models.enums import SymbolType

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.environ.get("BINANCE_TH_LIVE") != "1",
        reason="set BINANCE_TH_LIVE=1 to run live user-data smoke tests",
    ),
    pytest.mark.skipif(
        BinanceThConfig().api_key is None,
        reason="set BINANCE_TH_API_KEY to run the live user-data smoke",
    ),
]


class TestLiveUserData:
    async def test_listenkey_lifecycle_and_connect(self) -> None:
        """POST listenKey -> connect /ws/<key> -> (context exit) keepalive stops + DELETE, clean close."""
        async with BinanceThClient() as client:
            user_stream = client.user_stream
            await user_stream._ensure_started()  # POST listenKey + open per-type connections
            assert user_stream._keys.key_for(SymbolType.GLOBAL) is not None or (
                user_stream._keys.key_for(SymbolType.SITE) is not None
            )
            # wait for at least one socket to actually connect to the WSA host
            for _ in range(80):
                if any(conn._ws is not None for conn in user_stream._conns):
                    break
                await asyncio.sleep(0.1)
            assert any(conn._ws is not None for conn in user_stream._conns)
        # exiting the context DELETEs the key(s) and closes the sockets — no unclosed-connector warning
