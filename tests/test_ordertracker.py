"""Tests for the reconciled local order tracker (ADR-0008 drop->reconcile).

Fully offline: list-backed async iterators + a fake open_orders provider, no sockets.
"""

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from binance_th.models.orders import Order
from binance_th.models.userdata import ExecutionReportEvent, order_from_execution_report
from binance_th.ordertracker import (
    _RECONNECTED,
    LocalOrderView,
    OrderTracker,
    OrderTrackerSynchronizer,
)


def _er(order_id: int, *, status: str = "NEW", update_time: int = 1) -> ExecutionReportEvent:
    return ExecutionReportEvent.model_validate(
        {
            "e": "executionReport",
            "E": update_time,
            "s": "BTCTHB",
            "c": f"c{order_id}",
            "S": "BUY",
            "o": "LIMIT",
            "f": "GTC",
            "q": "1",
            "p": "100",
            "x": "NEW",
            "X": status,
            "i": order_id,
            "l": "0",
            "z": "0",
            "L": "0",
            "T": update_time,
        }
    )


def _order(order_id: int, *, status: str = "NEW", update_time: int = 1) -> Order:
    return order_from_execution_report(_er(order_id, status=status, update_time=update_time))


async def _aiter(items: list[Any]) -> AsyncIterator[Any]:
    for item in items:
        yield item


class FakeOpenOrders:
    """Returns successive snapshots (clamped to the last); counts calls."""

    def __init__(self, snapshots: list[list[Order]]) -> None:
        self._snaps = snapshots
        self.calls = 0

    async def __call__(self, *_args: object, **_kwargs: object) -> list[Order]:
        snap = self._snaps[min(self.calls, len(self._snaps) - 1)]
        self.calls += 1
        return list(snap)


async def _capture(sync: OrderTrackerSynchronizer, events: list[Any]) -> list[set[int]]:
    return [{order.order_id for order in view.open()} async for view in sync.run(_aiter(events))]


class TestLocalOrderView:
    def test_seed_keeps_active_only(self) -> None:
        view = LocalOrderView()
        view.seed([_order(1, status="NEW"), _order(2, status="FILLED")])
        assert {o.order_id for o in view.open()} == {1}  # FILLED is not active

    def test_apply_upserts_then_removes_terminal(self) -> None:
        view = LocalOrderView()
        view.seed([])
        view.apply(_er(1, status="NEW", update_time=1))
        assert view.get(1) is not None
        view.apply(_er(1, status="PARTIALLY_FILLED", update_time=2))
        assert view.get(1).status.value == "PARTIALLY_FILLED"
        view.apply(_er(1, status="FILLED", update_time=3))
        assert view.get(1) is None  # terminal -> removed

    def test_monotonic_guard_drops_stale_report(self) -> None:
        view = LocalOrderView()
        view.apply(_er(1, status="PARTIALLY_FILLED", update_time=5))
        view.apply(_er(1, status="NEW", update_time=2))  # older -> ignored
        assert view.get(1).status.value == "PARTIALLY_FILLED"


class TestSynchronizer:
    async def test_seed_then_apply_events(self) -> None:
        provider = FakeOpenOrders([[_order(1)]])
        sync = OrderTrackerSynchronizer(open_orders_provider=provider)
        captures = await _capture(
            sync, [_er(2, status="NEW"), _er(1, status="FILLED", update_time=9)]
        )
        assert provider.calls == 1
        assert captures[0] == {1}  # REST seed exposed immediately
        assert captures[-1] == {2}  # order 1 filled -> removed, order 2 added

    async def test_reconnect_reseeds_and_replaces(self) -> None:
        provider = FakeOpenOrders([[_order(1)], [_order(3)]])
        sync = OrderTrackerSynchronizer(open_orders_provider=provider)
        captures = await _capture(sync, [_er(2, status="NEW"), _RECONNECTED])
        assert provider.calls == 2  # re-seeded on reconnect
        assert {1, 2} in captures  # order 2 was tracked (atop the seed) before the drop
        assert captures[-1] == {3}  # post-reconnect view == the REST snapshot (replace)


class TestOrderTracker:
    async def test_syncs_and_reads(self) -> None:
        provider = FakeOpenOrders([[_order(1), _order(2)]])
        tracker = OrderTracker(events=_aiter([]), open_orders_provider=provider)
        assert tracker.open() == []  # not started yet
        tracker.start()
        await asyncio.wait_for(tracker.wait_synced(), timeout=1.0)
        assert tracker.synced
        assert {o.order_id for o in tracker.open()} == {1, 2}
        assert tracker.get(1) is not None
        await tracker.aclose()

    async def test_aclose_cancels_runs_on_close_and_is_idempotent(self) -> None:
        closed = []

        async def on_close() -> None:
            closed.append(True)

        async def _hanging() -> AsyncIterator[Any]:
            await asyncio.Event().wait()
            yield None  # pragma: no cover - never reached

        provider = FakeOpenOrders([[_order(1)]])
        tracker = OrderTracker(events=_hanging(), open_orders_provider=provider, on_close=on_close)
        tracker.start()
        await asyncio.wait_for(tracker.wait_synced(), timeout=1.0)
        await tracker.aclose()
        await tracker.aclose()  # idempotent
        assert closed == [True]  # on_close ran exactly once
