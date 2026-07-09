"""Tests for the WebSocket stream client, router, and connection supervisor (M5).

Fully offline: a scripted ``FakeConnect``/``FakeWsConnection`` stands in for the
``websockets`` connection, so reconnect, demux, backpressure, and teardown are all
exercised without a network.
"""

import asyncio
import json
import warnings
from decimal import Decimal
from typing import Any

import pytest

from binance_th.config import BinanceThConfig
from binance_th.exceptions import BinanceThWebSocketError
from binance_th.models.base import SymbolTypeInfo
from binance_th.models.market import OrderBook, OrderBookEntry
from binance_th.stream import StreamClient, StreamRouter, _Connection, _Subscription

GSTREAM = "wss://www.binance.th/gstream"
NSTREAM = "wss://www.binance.th/nstream"

# --- fakes ----------------------------------------------------------------------------


class FakeWsConnection:
    """Scripted stand-in for a websockets connection."""

    def __init__(self, frames: list[str], *, on_empty: str = "hang") -> None:
        self._frames = list(frames)
        self._on_empty = on_empty  # "hang" | "stop" | "raise"
        self.sent: list[str] = []
        self.closed = False
        self._closed_event = asyncio.Event()

    async def send(self, message: str) -> None:
        self.sent.append(message)

    async def close(self) -> None:
        self.closed = True
        self._closed_event.set()

    def __aiter__(self) -> "FakeWsConnection":
        return self

    async def __anext__(self) -> str:
        if self._frames:
            return self._frames.pop(0)
        if self._on_empty == "stop":
            raise StopAsyncIteration
        if self._on_empty == "raise":
            raise ConnectionError("fake socket closed")
        await self._closed_event.wait()  # "hang": stay open until closed
        raise StopAsyncIteration


class FakeConnect:
    """Injectable connect seam: hands out scripted connections and records URLs."""

    def __init__(
        self, scripts: list[tuple[list[str], str]] | None = None, *, fail_first: int = 0
    ) -> None:
        self._scripts = list(scripts or [])
        self._fail_first = fail_first
        self.attempts = 0
        self.urls: list[str] = []
        self.conns: list[FakeWsConnection] = []

    async def __call__(self, url: str, **_kwargs: float) -> FakeWsConnection:
        self.attempts += 1
        self.urls.append(url)
        if self.attempts <= self._fail_first:
            raise ConnectionError("fake connect failed")
        idx = len(self.conns)
        frames, on_empty = self._scripts[idx] if idx < len(self._scripts) else ([], "hang")
        conn = FakeWsConnection(frames, on_empty=on_empty)
        self.conns.append(conn)
        return conn


class FakeSymbolTypes:
    def __init__(self, mapping: dict[str, str]) -> None:
        self.mapping = mapping
        self.calls = 0

    async def __call__(self, *, symbol: str | None = None) -> list[SymbolTypeInfo]:
        self.calls += 1
        sym = symbol or ""
        stype = self.mapping.get(sym.upper(), "SITE")
        return [SymbolTypeInfo(symbol=sym, symbol_type=stype)]


class FakeDepth:
    def __init__(self, snapshot: OrderBook) -> None:
        self.snapshot = snapshot
        self.calls = 0

    async def __call__(self, *_args: object, **_kwargs: object) -> OrderBook:
        self.calls += 1
        return self.snapshot


def _frame(stream: str, data: dict[str, Any]) -> str:
    return json.dumps({"stream": stream, "data": data})


async def _instant_sleep(_seconds: float) -> None:
    await asyncio.sleep(0)


def _make_client(
    connect: FakeConnect,
    *,
    config: BinanceThConfig | None = None,
    depth: FakeDepth | None = None,
    types: dict[str, str] | None = None,
) -> StreamClient:
    snap = OrderBook(last_update_id=1, bids=[], asks=[])
    return StreamClient(
        config=config or BinanceThConfig(),
        depth_provider=depth or FakeDepth(snap),
        symbol_type_provider=FakeSymbolTypes(types or {"BTCUSDT": "GLOBAL", "BTCTHB": "SITE"}),
        connect=connect,
        sleep=_instant_sleep,
        session_ttl=100.0,
    )


async def _settle(pred: Any, *, steps: int = 1000) -> None:
    for _ in range(steps):
        if pred():
            return
        await asyncio.sleep(0)
    raise AssertionError("condition not met within budget")


TRADE = {"e": "trade", "E": 1, "T": 1, "s": "BTCTHB", "t": 5, "p": "100", "q": "1", "m": True}
DEPTH = {"e": "depthUpdate", "E": 1, "s": "BTCTHB", "U": 100, "u": 101, "b": [["10", "2"]], "a": []}


# --- router ---------------------------------------------------------------------------


class TestStreamRouter:
    def test_stream_name(self) -> None:
        r = StreamRouter(config=BinanceThConfig(), symbol_type_provider=FakeSymbolTypes({}))
        assert r.stream_name("BTCTHB", "depth") == "btcthb@depth"
        assert r.stream_name("BTCTHB", "kline", interval="1m") == "btcthb@kline_1m"

    def test_combined_url_is_sorted(self) -> None:
        r = StreamRouter(config=BinanceThConfig(), symbol_type_provider=FakeSymbolTypes({}))
        assert (
            r.combined_url("wss://h", ["b@trade", "a@depth"]) == "wss://h?streams=a@depth/b@trade"
        )

    async def test_host_for_and_cache(self) -> None:
        types = FakeSymbolTypes({"BTCUSDT": "GLOBAL", "BTCTHB": "SITE"})
        r = StreamRouter(config=BinanceThConfig(), symbol_type_provider=types)
        assert await r.host_for("BTCUSDT") == GSTREAM
        assert await r.host_for("BTCTHB") == NSTREAM
        await r.host_for("BTCUSDT")  # cached
        assert types.calls == 2  # once per distinct symbol


# --- demux / dispatch (unit) ----------------------------------------------------------


class TestDispatch:
    def _conn(self) -> _Connection:
        return _Connection(
            host=NSTREAM,
            router=StreamRouter(config=BinanceThConfig(), symbol_type_provider=FakeSymbolTypes({})),
            config=BinanceThConfig(),
            connect=FakeConnect(),
            sleep=_instant_sleep,
            session_ttl=100.0,
        )

    async def test_demux_and_skips(self) -> None:
        conn = self._conn()
        sub_t = _Subscription("btcthb@trade")
        sub_d = _Subscription("btcthb@depth")
        conn._subs["btcthb@trade"] = [sub_t]
        conn._subs["btcthb@depth"] = [sub_d]
        conn._dispatch(_frame("btcthb@trade", TRADE))
        conn._dispatch(_frame("btcthb@depth", DEPTH))
        conn._dispatch("not json")  # malformed -> skipped
        conn._dispatch(json.dumps({"result": None, "id": 1}))  # control ack -> skipped
        conn._dispatch(_frame("btcthb@unknown", {"x": 1}))  # no subscriber -> dropped
        assert (await sub_t.__anext__())["p"] == "100"
        assert (await sub_d.__anext__())["s"] == "BTCTHB"
        # only one payload each was delivered
        assert sub_t._queue.empty()
        assert sub_d._queue.empty()

    async def test_fan_out_to_multiple_subscribers(self) -> None:
        conn = self._conn()
        sub1 = _Subscription("btcthb@trade")
        sub2 = _Subscription("btcthb@trade")
        conn._subs["btcthb@trade"] = [sub1, sub2]
        conn._dispatch(_frame("btcthb@trade", TRADE))
        assert (await sub1.__anext__())["p"] == "100"
        assert (await sub2.__anext__())["p"] == "100"

    async def test_unsubscribe_is_ref_counted(self) -> None:
        conn = self._conn()
        conn._ws = None  # no live socket -> unsubscribe won't try to send a control frame
        sub1 = _Subscription("btcthb@trade")
        sub2 = _Subscription("btcthb@trade")
        conn._subs["btcthb@trade"] = [sub1, sub2]
        conn.desired.add("btcthb@trade")
        await conn.unsubscribe(sub1)
        assert "btcthb@trade" in conn.desired  # still one subscriber left
        await conn.unsubscribe(sub2)
        assert "btcthb@trade" not in conn.desired  # last one -> stream removed


# --- subscription backpressure --------------------------------------------------------


class TestSubscription:
    async def test_drop_oldest_ring(self) -> None:
        sub = _Subscription("s", maxsize=2)
        sub.offer({"n": 1})
        sub.offer({"n": 2})
        sub.offer({"n": 3})  # full -> drop oldest (n=1)
        assert sub.lagged == 1
        assert (await sub.__anext__())["n"] == 2
        assert (await sub.__anext__())["n"] == 3

    async def test_close_ends_iteration(self) -> None:
        sub = _Subscription("s")
        sub.close()
        with pytest.raises(StopAsyncIteration):
            await sub.__anext__()

    async def test_fault_raises(self) -> None:
        sub = _Subscription("s")
        sub.fault(BinanceThWebSocketError("boom"))
        with pytest.raises(BinanceThWebSocketError):
            await sub.__anext__()


# --- StreamClient end-to-end ----------------------------------------------------------


class TestStreamClient:
    async def test_watch_trades_yields_typed_events(self) -> None:
        fc = FakeConnect([([_frame("btcthb@trade", TRADE)], "hang")])
        client = _make_client(fc)
        agen = client.watch_trades("BTCTHB")
        ev = await agen.__anext__()
        assert ev.price == Decimal("100")
        assert ev.symbol == "BTCTHB"
        assert fc.urls[0] == f"{NSTREAM}?streams=btcthb@trade"
        await agen.aclose()
        await client.aclose()

    async def test_watch_klines_url_carries_interval(self) -> None:
        kline = {"e": "kline", "E": 1, "s": "BTCTHB", "k": {
            "t": 1, "T": 2, "s": "BTCTHB", "i": "1m", "f": 1, "L": 2, "o": "1", "c": "2",
            "h": "3", "l": "0", "v": "1", "n": 1, "x": False, "q": "1", "V": "1", "Q": "1", "B": "0",
        }}  # fmt: skip
        fc = FakeConnect([([_frame("btcthb@kline_1m", kline)], "hang")])
        client = _make_client(fc)
        agen = client.watch_klines("BTCTHB", "1m")
        ev = await agen.__anext__()
        assert ev.kline.interval == "1m"
        assert fc.urls[0] == f"{NSTREAM}?streams=btcthb@kline_1m"
        await agen.aclose()
        await client.aclose()

    async def test_global_and_site_use_separate_connections(self) -> None:
        fc = FakeConnect()
        client = _make_client(fc)
        await client._subscribe("BTCUSDT", "trade")
        await client._subscribe("BTCTHB", "trade")
        await _settle(lambda: len(fc.conns) >= 2)
        assert set(client._conns) == {GSTREAM, NSTREAM}
        assert fc.urls[0].startswith(GSTREAM)
        assert any(u.startswith(NSTREAM) for u in fc.urls)
        await client.aclose()

    async def test_dynamic_subscribe_sends_control_frame(self) -> None:
        fc = FakeConnect()  # single hanging connection
        client = _make_client(fc)
        conn, _sub1 = await client._subscribe("BTCTHB", "trade")
        await _settle(lambda: conn._ws is not None)
        conn2, _sub2 = await client._subscribe("BTCTHB", "depth")
        assert conn2 is conn  # same host -> same connection
        await _settle(lambda: len(fc.conns[0].sent) >= 1)
        sent = fc.conns[0].sent
        assert any('"SUBSCRIBE"' in s and "btcthb@depth" in s for s in sent)
        await client.aclose()

    async def test_reconnect_rebuilds_url(self) -> None:
        # first socket ends immediately (stop) -> supervisor reconnects with the rebuilt URL
        fc = FakeConnect([([], "stop")])
        client = _make_client(fc)  # ws_auto_reconnect defaults True
        await client._subscribe("BTCTHB", "trade")
        await _settle(lambda: len(fc.conns) >= 2)
        assert fc.urls[0] == fc.urls[1] == f"{NSTREAM}?streams=btcthb@trade"
        await client.aclose()

    async def test_no_reconnect_faults_consumer(self) -> None:
        fc = FakeConnect([([], "stop")])
        client = _make_client(fc, config=BinanceThConfig(ws_auto_reconnect=False))
        with pytest.raises(BinanceThWebSocketError):
            async for _ev in client.watch_trades("BTCTHB"):
                pass
        await client.aclose()

    async def test_order_book_syncs_and_unsubscribes_on_close(self) -> None:
        snap = OrderBook(
            last_update_id=100,
            bids=[OrderBookEntry(price=Decimal("10"), quantity=Decimal("1"))],
            asks=[OrderBookEntry(price=Decimal("11"), quantity=Decimal("1"))],
        )
        fc = FakeConnect([([_frame("btcthb@depth", DEPTH)], "hang")])
        client = _make_client(fc, depth=FakeDepth(snap))
        book = await client.order_book("BTCTHB")
        await asyncio.wait_for(book.wait_synced(), timeout=1.0)
        await _settle(lambda: book.best_bid() == (Decimal("10"), Decimal("2")))
        assert book.best_ask() == (Decimal("11"), Decimal("1"))
        await book.aclose()
        assert "btcthb@depth" not in client._conns[NSTREAM].desired
        await client.aclose()

    async def test_watch_helpers_decode_each_channel(self) -> None:
        agg = {"e": "aggTrade", "E": 1, "T": 1, "s": "BTCTHB", "a": 9,
               "p": "100", "q": "1", "f": 1, "l": 2, "m": True}  # fmt: skip
        book = {"u": 5, "s": "BTCTHB", "b": "1", "B": "2", "a": "3", "A": "4"}
        tick = {"e": "24hrTicker", "E": 1, "s": "BTCTHB", "c": "100"}
        cases = [
            ("watch_depth", "btcthb@depth", DEPTH, lambda e: e.final_update_id == 101),
            ("watch_agg_trades", "btcthb@aggTrade", agg, lambda e: e.agg_trade_id == 9),
            ("watch_book_ticker", "btcthb@bookTicker", book, lambda e: e.bid_price == Decimal("1")),
            ("watch_ticker", "btcthb@ticker", tick, lambda e: e.last_price == Decimal("100")),
        ]
        for method, stream, data, check in cases:
            fc = FakeConnect([([_frame(stream, data)], "hang")])
            client = _make_client(fc)
            agen = getattr(client, method)("BTCTHB")
            ev = await agen.__anext__()
            assert check(ev)
            assert fc.urls[0] == f"{NSTREAM}?streams={stream}"
            await agen.aclose()
            await client.aclose()

    async def test_connect_failure_then_reconnects(self) -> None:
        fc = FakeConnect(fail_first=1)  # first connect raises, then a hanging connection
        client = _make_client(fc)
        await client._subscribe("BTCTHB", "trade")
        await _settle(lambda: len(fc.conns) >= 1 and fc.attempts >= 2)
        assert fc.attempts >= 2  # retried after the failure
        await client.aclose()

    async def test_connect_failure_without_reconnect_faults(self) -> None:
        fc = FakeConnect(fail_first=1)
        client = _make_client(fc, config=BinanceThConfig(ws_auto_reconnect=False))
        with pytest.raises(BinanceThWebSocketError):
            async for _ev in client.watch_trades("BTCTHB"):
                pass
        await client.aclose()

    async def test_dynamic_subscribe_reconnects_when_frames_unsupported(self) -> None:
        cfg = BinanceThConfig(ws_supports_live_subscribe=False)
        fc = FakeConnect()  # connections hang
        client = _make_client(fc, config=cfg)
        conn, _sub = await client._subscribe("BTCTHB", "trade")
        await _settle(lambda: conn._ws is not None)
        await client._subscribe("BTCTHB", "depth")  # forces a reconnect to rebuild the URL
        await _settle(lambda: len(fc.conns) >= 2)
        assert fc.urls[-1] == f"{NSTREAM}?streams=btcthb@depth/btcthb@trade"
        await client.aclose()

    async def test_aclose_is_clean_and_idempotent(self) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("error", ResourceWarning)
            fc = FakeConnect([([_frame("btcthb@trade", TRADE)], "hang")])
            client = _make_client(fc)
            agen = client.watch_trades("BTCTHB")
            await agen.__anext__()
            await agen.aclose()
            await client.aclose()
            await client.aclose()  # idempotent
            assert fc.conns[0].closed
