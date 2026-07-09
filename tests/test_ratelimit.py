"""Tests for the dual-window rate limiter (ADR-0005)."""

import pytest

from binance_th.models.base import RateLimit
from binance_th.models.enums import RateLimitInterval, RateLimitType
from binance_th.ratelimit import DualWindowRateLimiter

from .conftest import FakeTime

_WEIGHT_MIN = (RateLimitType.REQUEST_WEIGHT, RateLimitInterval.MINUTE, 1)
_ORDERS_10S = (RateLimitType.ORDERS, RateLimitInterval.SECOND, 10)
_ORDERS_MIN = (RateLimitType.ORDERS, RateLimitInterval.MINUTE, 1)


def _rule(rate_type: RateLimitType, interval: RateLimitInterval, num: int, limit: int) -> RateLimit:
    return RateLimit(rate_limit_type=rate_type, interval=interval, interval_num=num, limit=limit)


def _limiter(rules: list[RateLimit], ft: FakeTime) -> DualWindowRateLimiter:
    return DualWindowRateLimiter.from_rate_limits(rules, clock=ft.clock, sleep=ft.sleep)


class TestAcquire:
    """Blocking/pacing behavior."""

    async def test_weight_window_blocks_and_releases(self) -> None:
        """The (limit+1)th weight unit waits for the window to roll over."""
        ft = FakeTime()
        limiter = _limiter(
            [_rule(RateLimitType.REQUEST_WEIGHT, RateLimitInterval.SECOND, 1, 5)], ft
        )
        for _ in range(5):
            await limiter.acquire(1, mutating=False)
        assert ft.sleeps == []
        await limiter.acquire(1, mutating=False)
        assert ft.sleeps == [pytest.approx(1.0)]

    async def test_weight_charges_by_weight_not_one(self) -> None:
        """A weight-N call charges N, not 1."""
        ft = FakeTime()
        limiter = _limiter(
            [_rule(RateLimitType.REQUEST_WEIGHT, RateLimitInterval.SECOND, 1, 10)], ft
        )
        await limiter.acquire(10, mutating=False)
        await limiter.acquire(1, mutating=False)
        assert ft.sleeps == [pytest.approx(1.0)]

    async def test_order_window_charges_only_mutating(self) -> None:
        """Reads never touch the order window; only mutating calls do."""
        ft = FakeTime()
        limiter = _limiter([_rule(RateLimitType.ORDERS, RateLimitInterval.MINUTE, 1, 2)], ft)
        for _ in range(10):
            await limiter.acquire(5, mutating=False)
        assert ft.sleeps == []
        await limiter.acquire(1, mutating=True)
        await limiter.acquire(1, mutating=True)
        assert ft.sleeps == []
        await limiter.acquire(1, mutating=True)
        assert len(ft.sleeps) == 1

    async def test_multi_window_both_must_admit(self) -> None:
        """When two windows apply, the tighter one gates."""
        ft = FakeTime()
        limiter = _limiter(
            [
                _rule(RateLimitType.ORDERS, RateLimitInterval.MINUTE, 1, 1000),
                _rule(RateLimitType.ORDERS, RateLimitInterval.SECOND, 10, 5),
            ],
            ft,
        )
        for _ in range(5):
            await limiter.acquire(1, mutating=True)
        assert ft.sleeps == []
        await limiter.acquire(1, mutating=True)  # 10s window full; 60s has room
        assert ft.sleeps == [pytest.approx(10.0)]
        assert limiter._windows[_ORDERS_MIN].used == 6  # 60s counter persisted across the 10s roll

    async def test_oversized_charge_makes_progress(self) -> None:
        """A single charge larger than the limit still admits on a fresh window."""
        ft = FakeTime()
        limiter = _limiter(
            [_rule(RateLimitType.REQUEST_WEIGHT, RateLimitInterval.SECOND, 1, 5)], ft
        )
        await limiter.acquire(100, mutating=False)
        assert ft.sleeps == []


class TestHeaderReconciliation:
    """update_from_headers behavior."""

    def test_raises_usage_up_only(self) -> None:
        """A higher server value raises local usage; a lower one is ignored."""
        ft = FakeTime()
        limiter = _limiter(
            [_rule(RateLimitType.REQUEST_WEIGHT, RateLimitInterval.MINUTE, 1, 6000)], ft
        )
        limiter.update_from_headers({"x-mbx-used-weight-1m": "5000"})
        limiter.update_from_headers({"x-mbx-used-weight-1m": "10"})
        assert limiter._windows[_WEIGHT_MIN].used == 5000

    def test_family_parsing_case_insensitive_unknown_ignored(self) -> None:
        """Weight and order families parse case-insensitively; unknown windows are skipped."""
        ft = FakeTime()
        limiter = _limiter(
            [
                _rule(RateLimitType.REQUEST_WEIGHT, RateLimitInterval.MINUTE, 1, 6000),
                _rule(RateLimitType.ORDERS, RateLimitInterval.SECOND, 10, 1000),
            ],
            ft,
        )
        limiter.update_from_headers(
            {
                "X-MBX-USED-WEIGHT-1M": "100",
                "x-mbx-order-count-10s": "50",
                "x-mbx-used-weight-1h": "999",  # no such window
                "content-type": "application/json",
                "x-mbx-used-weight-1m": "notanint",  # unparseable → ignored
            }
        )
        assert limiter._windows[_WEIGHT_MIN].used == 100
        assert limiter._windows[_ORDERS_10S].used == 50


class TestSeeding:
    """from_defaults and reseed."""

    def test_from_defaults_builds_verified_windows(self) -> None:
        """The default limiter has exactly the three verified windows."""
        limiter = DualWindowRateLimiter.from_defaults()
        assert set(limiter._windows) == {_WEIGHT_MIN, _ORDERS_MIN, _ORDERS_10S}
        assert limiter._windows[_WEIGHT_MIN].limit == 6000
        assert limiter._windows[_ORDERS_10S].duration == 10.0

    def test_reseed_preserves_hot_counter(self) -> None:
        """reseed carries over used/window_start for kept keys and adds new ones."""
        ft = FakeTime()
        limiter = _limiter(
            [_rule(RateLimitType.REQUEST_WEIGHT, RateLimitInterval.MINUTE, 1, 6000)], ft
        )
        limiter.update_from_headers({"x-mbx-used-weight-1m": "5000"})
        start = limiter._windows[_WEIGHT_MIN].window_start
        limiter.reseed(
            [
                _rule(RateLimitType.REQUEST_WEIGHT, RateLimitInterval.MINUTE, 1, 12000),
                _rule(RateLimitType.ORDERS, RateLimitInterval.SECOND, 10, 1000),
            ]
        )
        kept = limiter._windows[_WEIGHT_MIN]
        assert kept.used == 5000
        assert kept.window_start == start
        assert kept.limit == 12000
        assert _ORDERS_10S in limiter._windows
