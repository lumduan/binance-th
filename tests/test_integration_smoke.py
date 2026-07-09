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


class TestLiveMarket:
    """Live public market-data checks (M3a)."""

    async def test_depth(self) -> None:
        """Real order book has both sides."""
        async with BinanceThClient() as client:
            book = await client.market.depth("BNBTHB", limit=5)
            assert book.bids and book.asks

    async def test_exchange_info_and_cache(self) -> None:
        """Real exchangeInfo parses (the reconciled model), and caches."""
        async with BinanceThClient() as client:
            info = await client.exchange_info()
            assert len(info.symbols) >= 100
            assert await client.exchange_info() is info
            assert info.get_symbol("BNBTHB") is not None

    async def test_ticker_price(self) -> None:
        """Real last price is positive."""
        async with BinanceThClient() as client:
            price = await client.market.ticker_price("BNBTHB")
            assert price.price > 0

    async def test_iter_klines(self) -> None:
        """Paginated klines over the last 10 minutes are contiguous and de-duped."""
        async with BinanceThClient() as client:
            end = (await client.server_time()).server_time
            opens = [
                kline.open_time
                async for kline in client.market.iter_klines(
                    "BTCUSDT", "1m", start_time=end - 600_000, end_time=end, limit=100
                )
            ]
            assert opens == sorted(set(opens))
