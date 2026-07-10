"""Opt-in live WebSocket smoke test against the real Binance TH streams (M5).

Skipped unless ``BINANCE_TH_LIVE=1`` so CI stays offline (the env-var guard is the
real gate — CI runs a bare ``pytest`` that does not deselect the ``integration`` mark).
Run locally with::

    BINANCE_TH_LIVE=1 uv run pytest -m integration -k ws_smoke

Public market streams only — no credentials. Real money is never touched.
"""

import asyncio
import os

import pytest

from binance_th import BinanceThClient

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.environ.get("BINANCE_TH_LIVE") != "1",
        reason="set BINANCE_TH_LIVE=1 to run live WebSocket smoke tests",
    ),
]

_SYMBOL = "BTCTHB"  # liquid SITE symbol (streams on /nstream)
_TIMEOUT = 25.0


class TestLiveWebSocket:
    """Live checks that the stream client decodes real frames and syncs a book."""

    async def test_watch_depth_yields_an_event(self) -> None:
        async with BinanceThClient() as client:
            stream = client.ws.watch_depth(_SYMBOL)
            try:
                event = await asyncio.wait_for(stream.__anext__(), timeout=_TIMEOUT)
                assert event.symbol.upper() == _SYMBOL
                assert event.final_update_id >= event.first_update_id
            finally:
                await stream.aclose()

    async def test_order_book_syncs(self) -> None:
        async with BinanceThClient() as client:
            book = await client.ws.order_book(_SYMBOL)
            try:
                await asyncio.wait_for(book.wait_synced(), timeout=_TIMEOUT)
                best_bid = book.best_bid()
                best_ask = book.best_ask()
                assert best_bid is not None
                assert best_ask is not None
                assert best_bid[0] < best_ask[0]  # a real book is not crossed
            finally:
                await book.aclose()
