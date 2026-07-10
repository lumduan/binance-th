"""Tests for the local order-book sync engine (ADR-0007).

Fully offline: the sync loop is driven by list-backed async iterators and a fake
depth-snapshot provider — no WebSocket involvement.
"""

import asyncio
from collections.abc import AsyncIterator
from decimal import Decimal
from typing import Any

import pytest

from binance_th.models.market import OrderBook, OrderBookEntry
from binance_th.models.stream import DepthUpdateEvent
from binance_th.orderbook import LocalOrderBook, ManagedOrderBook, OrderBookSynchronizer

# --- helpers --------------------------------------------------------------------------


def _snapshot(
    last_update_id: int,
    *,
    bids: list[tuple[str, str]],
    asks: list[tuple[str, str]],
) -> OrderBook:
    return OrderBook(
        last_update_id=last_update_id,
        bids=[OrderBookEntry(price=Decimal(p), quantity=Decimal(q)) for p, q in bids],
        asks=[OrderBookEntry(price=Decimal(p), quantity=Decimal(q)) for p, q in asks],
    )


def _delta(
    first_id: int,
    final_id: int,
    *,
    bids: list[list[str]] | None = None,
    asks: list[list[str]] | None = None,
) -> DepthUpdateEvent:
    payload: dict[str, Any] = {
        "e": "depthUpdate",
        "E": 1,
        "s": "BTCTHB",
        "U": first_id,
        "u": final_id,
        "b": bids or [],
        "a": asks or [],
    }
    return DepthUpdateEvent.model_validate(payload)


async def _aiter(items: list[DepthUpdateEvent]) -> AsyncIterator[DepthUpdateEvent]:
    for item in items:
        yield item


class FakeDepth:
    """Injectable depth provider: returns queued snapshots, counts calls."""

    def __init__(self, snapshots: list[OrderBook]) -> None:
        self._snapshots = list(snapshots)
        self.calls = 0

    async def __call__(self, *_args: object, **_kwargs: object) -> OrderBook:
        self.calls += 1
        return self._snapshots.pop(0)


# State snapshot captured at each yield: (bids, asks, last_applied_u). Needed because the
# synchronizer yields one live-mutating book, so collecting the objects would show only the
# final state — copy the dicts to observe intermediate states.
State = tuple[dict[Decimal, Decimal], dict[Decimal, Decimal], int]


async def _capture(sync: OrderBookSynchronizer, deltas: list[DepthUpdateEvent]) -> list[State]:
    return [
        (dict(book.bids), dict(book.asks), book.last_applied_u)
        async for book in sync.run(_aiter(deltas))
    ]


# --- LocalOrderBook (pure) ------------------------------------------------------------


class TestLocalOrderBook:
    def test_seed_reads_and_ordering(self) -> None:
        book = LocalOrderBook("BTCTHB")
        book.seed(_snapshot(100, bids=[("10", "1"), ("9", "2")], asks=[("12", "3"), ("11", "1")]))
        assert book.best_bid() == (Decimal("10"), Decimal("1"))
        assert book.best_ask() == (Decimal("11"), Decimal("1"))
        assert book.bids_top(2) == [(Decimal("10"), Decimal("1")), (Decimal("9"), Decimal("2"))]
        assert book.asks_top(2) == [(Decimal("11"), Decimal("1")), (Decimal("12"), Decimal("3"))]
        assert book.last_applied_u == 100

    def test_apply_updates_removes_and_adds(self) -> None:
        book = LocalOrderBook("BTCTHB")
        book.seed(_snapshot(100, bids=[("10", "1"), ("9", "2")], asks=[("11", "1")]))
        # update 10, remove 9 (qty 0), add 9.5
        book.apply(_delta(101, 102, bids=[["10", "1.5"], ["9", "0"], ["9.5", "4"]]))
        assert book.bids[Decimal("10")] == Decimal("1.5")
        assert Decimal("9") not in book.bids
        assert book.best_bid() == (Decimal("10"), Decimal("1.5"))
        assert book.bids_top(2) == [(Decimal("10"), Decimal("1.5")), (Decimal("9.5"), Decimal("4"))]
        assert book.last_applied_u == 102

    def test_empty_book_reads(self) -> None:
        book = LocalOrderBook("X")
        assert book.best_bid() is None
        assert book.best_ask() is None
        assert book.bids_top(5) == []
        assert book.asks_top(5) == []


# --- OrderBookSynchronizer (state machine) --------------------------------------------


class TestSynchronizer:
    async def test_snapshot_exposed_then_deltas_applied_and_stale_dropped(self) -> None:
        depth = FakeDepth([_snapshot(100, bids=[("10", "1")], asks=[("11", "1")])])
        sync = OrderBookSynchronizer("BTCTHB", depth_provider=depth)
        states = await _capture(
            sync,
            [
                _delta(90, 99, bids=[["10", "5"]]),  # stale (u<=100) -> dropped
                _delta(100, 101, bids=[["10", "2"]]),  # first, brackets -> applied
                _delta(102, 103, asks=[["11", "0"]]),  # contiguous -> applied (removes ask)
            ],
        )
        assert depth.calls == 1
        # first yield is the raw snapshot; the stale delta was dropped (not yielded)
        assert states[0][0][Decimal("10")] == Decimal("1")
        assert len(states) == 3  # snapshot + 2 applied deltas
        bids, asks, last_u = states[-1]
        assert bids[Decimal("10")] == Decimal("2")
        assert Decimal("11") not in asks
        assert last_u == 103

    async def test_bracket_failure_triggers_resnapshot(self) -> None:
        depth = FakeDepth(
            [
                _snapshot(100, bids=[("10", "1")], asks=[]),
                _snapshot(200, bids=[("10", "9")], asks=[]),
            ]
        )
        sync = OrderBookSynchronizer("X", depth_provider=depth)
        # first non-stale delta starts at U=150, which does not bracket lastUpdateId 100
        states = await _capture(sync, [_delta(150, 160, bids=[["10", "2"]])])
        assert depth.calls == 2  # re-snapshotted
        assert states[-1][0][Decimal("10")] == Decimal("9")  # seeded from the 2nd snapshot

    async def test_update_id_gap_triggers_resnapshot(self) -> None:
        depth = FakeDepth(
            [
                _snapshot(100, bids=[("10", "1")], asks=[]),
                _snapshot(300, bids=[("10", "9")], asks=[]),
            ]
        )
        sync = OrderBookSynchronizer("X", depth_provider=depth)
        states = await _capture(
            sync,
            [
                _delta(101, 102, bids=[["10", "2"]]),  # brackets -> applied
                _delta(110, 120, bids=[["10", "3"]]),  # gap (110 > 103) -> re-snapshot
            ],
        )
        assert depth.calls == 2
        # the delta1 state was observed before the gap
        assert any(bids.get(Decimal("10")) == Decimal("2") for bids, _asks, _u in states)
        # final state is the 2nd snapshot
        assert states[-1][0][Decimal("10")] == Decimal("9")

    async def test_replay_matches_reference_book(self) -> None:
        depth = FakeDepth(
            [
                _snapshot(
                    1000,
                    bids=[("100", "1"), ("99", "2"), ("98", "3")],
                    asks=[("101", "1"), ("102", "2")],
                )
            ]
        )
        sync = OrderBookSynchronizer("X", depth_provider=depth)
        states = await _capture(
            sync,
            [
                _delta(1001, 1001, bids=[["100", "1.5"]]),  # update bid 100
                _delta(1002, 1003, bids=[["99", "0"]], asks=[["101", "0.5"]]),  # remove/adjust
                _delta(1004, 1004, bids=[["97", "5"]], asks=[["103", "4"]]),  # add levels
            ],
        )
        bids, asks, last_u = states[-1]
        assert bids == {
            Decimal("100"): Decimal("1.5"),
            Decimal("98"): Decimal("3"),
            Decimal("97"): Decimal("5"),
        }
        assert asks == {
            Decimal("101"): Decimal("0.5"),
            Decimal("102"): Decimal("2"),
            Decimal("103"): Decimal("4"),
        }
        assert last_u == 1004


# --- ManagedOrderBook (task wrapper) --------------------------------------------------


class TestManagedOrderBook:
    async def test_syncs_and_reads(self) -> None:
        depth = FakeDepth([_snapshot(100, bids=[("10", "1")], asks=[("11", "1")])])
        mob = ManagedOrderBook(
            "BTCTHB",
            deltas=_aiter([_delta(100, 101, bids=[["10", "2"]])]),
            depth_provider=depth,
        )
        assert mob.best_bid() is None  # not started yet
        assert mob.bids() == []
        mob.start()
        await asyncio.wait_for(mob.wait_synced(), timeout=1.0)
        assert mob.synced
        assert mob.best_bid() == (Decimal("10"), Decimal("2"))
        assert mob.best_ask() == (Decimal("11"), Decimal("1"))
        await mob.aclose()

    async def test_aclose_cancels_running_task_and_is_idempotent(self) -> None:
        depth = FakeDepth([_snapshot(100, bids=[("10", "1")], asks=[])])

        async def _blocking() -> AsyncIterator[DepthUpdateEvent]:
            # seed happens from the snapshot; then this blocks forever with no delta
            await asyncio.Event().wait()
            yield _delta(0, 0)  # pragma: no cover - never reached

        mob = ManagedOrderBook("X", deltas=_blocking(), depth_provider=depth)
        mob.start()
        await asyncio.wait_for(mob.wait_synced(), timeout=1.0)  # synced from the snapshot alone
        assert mob.synced
        assert mob._task is not None and not mob._task.done()
        await mob.aclose()
        await mob.aclose()  # idempotent, no error

    async def test_start_is_idempotent(self) -> None:
        depth = FakeDepth([_snapshot(100, bids=[("10", "1")], asks=[])])
        mob = ManagedOrderBook("X", deltas=_aiter([]), depth_provider=depth)
        mob.start()
        first = mob._task
        mob.start()
        assert mob._task is first
        await asyncio.wait_for(mob.wait_synced(), timeout=1.0)
        await mob.aclose()

    async def test_wait_synced_times_out_when_no_snapshot(self) -> None:
        # a depth provider that never returns keeps the book unsynced
        class HangingDepth:
            async def __call__(self, *_args: object, **_kwargs: object) -> OrderBook:
                await asyncio.Event().wait()
                raise AssertionError("unreachable")  # pragma: no cover

        mob = ManagedOrderBook("X", deltas=_aiter([]), depth_provider=HangingDepth())
        mob.start()
        with pytest.raises(TimeoutError):
            await asyncio.wait_for(mob.wait_synced(), timeout=0.05)
        assert not mob.synced
        await mob.aclose()
