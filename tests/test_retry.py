"""Tests for the backoff retryer (ADR-0012)."""

import pytest

from binance_th.exceptions import (
    BinanceThAuthError,
    BinanceThIPBannedError,
    BinanceThRateLimitError,
    BinanceThServerError,
)
from binance_th.retry import BackoffRetryer

from .conftest import FakeTime


def _always(_exc: BaseException) -> bool:
    return True


def _never(_exc: BaseException) -> bool:
    return False


def _retryer(ft: FakeTime, *, jitter_factor: float = 1.0) -> BackoffRetryer:
    return BackoffRetryer(jitter=lambda ceiling: ceiling * jitter_factor, sleep=ft.sleep)


class TestBackoffRetryer:
    """Schedule, jitter, Retry-After, and stop conditions."""

    async def test_backoff_schedule(self) -> None:
        """Exponential delays 0.5, 1, 2 before giving up after max_retries."""
        ft = FakeTime()

        async def fn() -> None:
            raise BinanceThServerError

        with pytest.raises(BinanceThServerError):
            await _retryer(ft).run(fn, retryable=_always, max_retries=3)
        assert ft.sleeps == [0.5, 1.0, 2.0]

    async def test_backoff_capped(self) -> None:
        """Delays are capped at 8 s."""
        ft = FakeTime()

        async def fn() -> None:
            raise BinanceThServerError

        with pytest.raises(BinanceThServerError):
            await _retryer(ft).run(fn, retryable=_always, max_retries=6)
        assert ft.sleeps == [0.5, 1.0, 2.0, 4.0, 8.0, 8.0]

    async def test_jitter_applied(self) -> None:
        """The jitter callable scales each delay ceiling."""
        ft = FakeTime()

        async def fn() -> None:
            raise BinanceThServerError

        with pytest.raises(BinanceThServerError):
            await _retryer(ft, jitter_factor=0.5).run(fn, retryable=_always, max_retries=2)
        assert ft.sleeps == [0.25, 0.5]

    async def test_success_after_retries(self) -> None:
        """A call that eventually succeeds returns its value."""
        ft = FakeTime()
        calls = {"n": 0}

        async def fn() -> str:
            calls["n"] += 1
            if calls["n"] < 3:
                raise BinanceThServerError
            return "ok"

        assert await _retryer(ft).run(fn, retryable=_always, max_retries=5) == "ok"
        assert calls["n"] == 3
        assert len(ft.sleeps) == 2

    async def test_non_retryable_stops_immediately(self) -> None:
        """A non-retryable error is raised on the first attempt with no sleep."""
        ft = FakeTime()

        async def fn() -> None:
            raise BinanceThAuthError

        with pytest.raises(BinanceThAuthError):
            await _retryer(ft).run(fn, retryable=_never, max_retries=3)
        assert ft.sleeps == []

    async def test_retry_after_honored_on_429(self) -> None:
        """A 429 sleeps its Retry-After, not the exponential delay."""
        ft = FakeTime()
        calls = {"n": 0}

        async def fn() -> str:
            calls["n"] += 1
            if calls["n"] == 1:
                raise BinanceThRateLimitError(retry_after=5)
            return "ok"

        assert await _retryer(ft).run(fn, retryable=_always, max_retries=3) == "ok"
        assert ft.sleeps == [5.0]

    async def test_retry_after_honored_on_418(self) -> None:
        """A 418 IP-ban honors its Retry-After."""
        ft = FakeTime()
        calls = {"n": 0}

        async def fn() -> str:
            calls["n"] += 1
            if calls["n"] == 1:
                raise BinanceThIPBannedError(retry_after=7)
            return "ok"

        assert await _retryer(ft).run(fn, retryable=_always, max_retries=3) == "ok"
        assert ft.sleeps == [7.0]

    async def test_missing_retry_after_uses_exponential(self) -> None:
        """An error without retry_after falls back to exponential backoff."""
        ft = FakeTime()
        calls = {"n": 0}

        async def fn() -> str:
            calls["n"] += 1
            if calls["n"] == 1:
                raise BinanceThServerError
            return "ok"

        assert await _retryer(ft).run(fn, retryable=_always, max_retries=3) == "ok"
        assert ft.sleeps == [0.5]

    async def test_max_retries_zero_is_single_attempt(self) -> None:
        """max_retries=0 tries once and never sleeps."""
        ft = FakeTime()

        async def fn() -> None:
            raise BinanceThServerError

        with pytest.raises(BinanceThServerError):
            await _retryer(ft).run(fn, retryable=_always, max_retries=0)
        assert ft.sleeps == []
