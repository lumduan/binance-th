"""Opt-in live smoke test against the real Binance TH public API.

Skipped unless ``BINANCE_TH_LIVE=1`` so CI stays offline. Run locally with::

    BINANCE_TH_LIVE=1 uv run pytest -m integration

These hit only public, unauthenticated endpoints (``/api/v1/ping`` and
``/api/v1/time``) — no credentials required.
"""

import os

import pytest

from binance_th import BinanceThClient

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.environ.get("BINANCE_TH_LIVE") != "1",
        reason="set BINANCE_TH_LIVE=1 to run live API smoke tests",
    ),
]


class TestLiveSmoke:
    """Live checks that the transport actually talks to Binance TH."""

    async def test_ping(self) -> None:
        """The live ping endpoint answers."""
        async with BinanceThClient() as client:
            assert await client.ping() is True

    async def test_server_time(self) -> None:
        """The live server time is a plausible recent epoch-ms value."""
        async with BinanceThClient() as client:
            server_time = await client.server_time()
            assert server_time.server_time > 1_600_000_000_000
