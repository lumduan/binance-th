"""Tests for the user-data stream client (M6).

Fully offline: a scripted bare-frame FakeConnect/FakeWsConnection, a fake ListenKeyManager,
and a fake open_orders provider — no sockets, no network.
"""

import asyncio
import json
import warnings
from decimal import Decimal
from typing import Any

import pytest

from binance_th.config import BinanceThConfig
from binance_th.exceptions import BinanceThAuthError, BinanceThWebSocketError
from binance_th.models.enums import SymbolType
from binance_th.models.orders import Order
from binance_th.models.userdata import ExecutionReportEvent, order_from_execution_report
from binance_th.userstream import UserDataStream

_WSA = "wss://nbstream.binance.th/w3w/wsa/stream"

ER: dict[str, Any] = {
    "e": "executionReport", "E": 1, "s": "BTCTHB", "c": "c1", "S": "BUY", "o": "LIMIT",
    "f": "GTC", "q": "1", "p": "100", "x": "NEW", "X": "NEW", "i": 7, "l": "0", "z": "0",
    "L": "0", "T": 1,
}  # fmt: skip
ACCT: dict[str, Any] = {
    "e": "outboundAccountPosition", "E": 1, "u": 1, "B": [{"a": "THB", "f": "100", "l": "0"}],
}  # fmt: skip
EXPIRED: dict[str, Any] = {"e": "listenKeyExpired", "E": 1}


def _bare(data: dict[str, Any]) -> str:
    return json.dumps(data)


class FakeWsConnection:
    def __init__(self, frames: list[str], *, on_empty: str = "hang") -> None:
        self._frames = list(frames)
        self._on_empty = on_empty
        self.closed = False
        self._closed_event = asyncio.Event()

    async def send(self, message: str) -> None:  # pragma: no cover - user-data never sends
        pass

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
        await self._closed_event.wait()
        raise StopAsyncIteration


class FakeConnect:
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


class FakeListenKeyManager:
    def __init__(self, *, keys: dict[SymbolType, str] | None = None) -> None:
        self._keys = keys or {SymbolType.GLOBAL: "GKEY", SymbolType.SITE: "SKEY"}
        self._cache: dict[SymbolType, str] = {}
        self.created = 0
        self.closed = 0

    async def create(self) -> None:
        self.created += 1
        self._cache = dict(self._keys)

    def key_for(self, symbol_type: SymbolType) -> str | None:
        return self._cache.get(symbol_type)

    async def keepalive(self) -> None:  # pragma: no cover
        pass

    async def close(self) -> None:
        self.closed += 1
        self._cache = {}


def _order(order_id: int) -> Order:
    return order_from_execution_report(ExecutionReportEvent.model_validate({**ER, "i": order_id}))


class FakeOpenOrders:
    def __init__(self, snapshots: list[list[Order]] | None = None) -> None:
        self._snaps = snapshots or [[]]
        self.calls = 0

    async def __call__(self, *_args: object, **_kwargs: object) -> list[Order]:
        snap = self._snaps[min(self.calls, len(self._snaps) - 1)]
        self.calls += 1
        return list(snap)


async def _instant_sleep(_seconds: float) -> None:
    await asyncio.sleep(0)


async def _settle(pred: Any, *, steps: int = 1000) -> None:
    for _ in range(steps):
        if pred():
            return
        await asyncio.sleep(0)
    raise AssertionError("condition not met")


def _make(
    connect: FakeConnect,
    *,
    keys: Any = None,
    open_orders: Any = None,
    config: BinanceThConfig | None = None,
) -> UserDataStream:
    return UserDataStream(
        config=config or BinanceThConfig(api_key="KEY"),
        transport=None,  # type: ignore[arg-type]  # unused: a fake ListenKeyManager is injected
        open_orders_provider=open_orders or FakeOpenOrders(),
        connect=connect,
        sleep=_instant_sleep,
        session_ttl=100.0,
        keys=keys or FakeListenKeyManager(),
    )


class TestUserDataStream:
    async def test_watch_orders_yields_and_uses_ws_url(self) -> None:
        fc = FakeConnect([([_bare(ER)], "hang")])  # the GLOBAL connection emits the report
        stream = _make(fc)
        agen = stream.watch_orders()
        event = await agen.__anext__()
        assert event.order_id == 7
        assert fc.urls[0] == f"{_WSA}/ws/GKEY"
        await agen.aclose()
        await stream.aclose()

    async def test_opens_one_connection_per_symbol_type(self) -> None:
        fc = FakeConnect()
        stream = _make(fc)
        await stream._ensure_started()
        await _settle(lambda: len(fc.conns) >= 2)
        assert {u.rsplit("/ws/", 1)[1] for u in fc.urls} == {"GKEY", "SKEY"}
        await stream.aclose()

    async def test_dispatch_routes_by_event_type(self) -> None:
        stream = _make(FakeConnect())
        orders = stream._subscribe("executionReport")
        account = stream._subscribe("outboundAccountPosition")
        stream._dispatch(ER)
        stream._dispatch(ACCT)
        stream._dispatch({"no": "event-type"})  # skipped
        assert (await orders.__anext__())["i"] == 7
        assert (await account.__anext__())["e"] == "outboundAccountPosition"
        await stream.aclose()

    async def test_watch_account_yields(self) -> None:
        fc = FakeConnect([([_bare(ACCT)], "hang")])
        stream = _make(fc)
        agen = stream.watch_account()
        event = await agen.__anext__()
        assert event.balances[0].asset == "THB"
        await agen.aclose()
        await stream.aclose()

    async def test_order_tracker_syncs_and_unsubscribes(self) -> None:
        fc = FakeConnect([([_bare(ER)], "hang")])
        stream = _make(fc, open_orders=FakeOpenOrders())
        tracker = await stream.order_tracker()
        await asyncio.wait_for(tracker.wait_synced(), timeout=1.0)
        await _settle(lambda: tracker.get(7) is not None)  # the NEW report was applied
        assert tracker.get(7).order_id == 7
        await tracker.aclose()
        assert "executionReport" not in stream._subs  # unsubscribed on close
        await stream.aclose()

    async def test_fail_fast_without_key(self) -> None:
        class NoKeyManager(FakeListenKeyManager):
            async def create(self) -> None:
                raise BinanceThAuthError("API key required")

        stream = _make(FakeConnect(), keys=NoKeyManager())
        with pytest.raises(BinanceThAuthError):
            async for _event in stream.watch_orders():
                pass
        await stream.aclose()

    async def test_listen_key_expired_triggers_reconnect(self) -> None:
        keys = FakeListenKeyManager(keys={SymbolType.GLOBAL: "GKEY"})  # GLOBAL only
        fc = FakeConnect([([_bare(EXPIRED)], "hang")])
        stream = _make(fc, keys=keys)
        await stream._ensure_started()
        await _settle(lambda: len(fc.conns) >= 2)  # expiry -> planned reconnect
        assert keys.created >= 2  # key recreated on reconnect
        assert all(u.endswith("/ws/GKEY") for u in fc.urls)
        await stream.aclose()

    async def test_watch_balances_yields(self) -> None:
        bal = {"e": "balanceUpdate", "E": 1, "a": "THB", "d": "-1.5", "T": 1}
        fc = FakeConnect([([_bare(bal)], "hang")])
        stream = _make(fc)
        agen = stream.watch_balances()
        event = await agen.__anext__()
        assert event.balance_delta == Decimal("-1.5")
        await agen.aclose()
        await stream.aclose()

    async def test_reconnect_reseeds_the_tracker(self) -> None:
        # GLOBAL connection drops immediately; open_orders returns order 7 on the 2nd (re-)seed
        keys = FakeListenKeyManager(keys={SymbolType.GLOBAL: "GKEY"})
        oo = FakeOpenOrders([[], [_order(7)]])
        fc = FakeConnect([([], "stop")])
        stream = _make(fc, keys=keys, open_orders=oo)
        tracker = await stream.order_tracker()
        await asyncio.wait_for(tracker.wait_synced(), timeout=1.0)  # seed 1 (empty)
        await _settle(lambda: oo.calls >= 2)  # drop -> broadcast reconcile -> re-seed
        await _settle(lambda: tracker.get(7) is not None)
        assert tracker.get(7).order_id == 7  # post-reconnect view == REST truth
        await stream.aclose()

    async def test_connect_failure_then_reconnects(self) -> None:
        keys = FakeListenKeyManager(keys={SymbolType.GLOBAL: "GKEY"})
        fc = FakeConnect(fail_first=1)
        stream = _make(fc, keys=keys)
        await stream._ensure_started()
        await _settle(lambda: fc.attempts >= 2 and len(fc.conns) >= 1)
        await stream.aclose()

    async def test_supervisor_retries_transient_create_failure(self) -> None:
        class FlakyKeys(FakeListenKeyManager):
            async def create(self) -> None:
                self.created += 1
                if self.created == 2:  # the GLOBAL supervisor's first create() fails once
                    raise RuntimeError("transient listenKey error")
                self._cache = dict(self._keys)

        keys = FlakyKeys(keys={SymbolType.GLOBAL: "GKEY"})
        stream = _make(FakeConnect(), keys=keys)
        await stream._ensure_started()
        await _settle(lambda: keys.created >= 3)  # ensure + failed + retried
        await stream.aclose()

    async def test_no_reconnect_faults_consumer(self) -> None:
        keys = FakeListenKeyManager(keys={SymbolType.GLOBAL: "GKEY"})
        fc = FakeConnect([([], "stop")])
        stream = _make(
            fc, keys=keys, config=BinanceThConfig(api_key="KEY", ws_auto_reconnect=False)
        )
        with pytest.raises(BinanceThWebSocketError):
            async for _event in stream.watch_orders():
                pass
        await stream.aclose()

    async def test_open_orders_snapshot(self) -> None:
        stream = _make(FakeConnect(), open_orders=FakeOpenOrders([[_order(3)]]))
        snapshot = await stream.open_orders_snapshot()
        assert [o.order_id for o in snapshot] == [3]
        await stream.aclose()

    async def test_aclose_deletes_key_no_warning_and_idempotent(self) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("error", ResourceWarning)
            keys = FakeListenKeyManager()
            fc = FakeConnect([([_bare(ER)], "hang")])
            stream = _make(fc, keys=keys)
            agen = stream.watch_orders()
            await agen.__anext__()
            await agen.aclose()
            await stream.aclose()
            await stream.aclose()  # idempotent
            assert keys.closed == 1  # listenKey DELETEd once
