"""M2 integration tests: limiter + retryer wired into the transport."""

import httpx
import pytest

from binance_th.config import BinanceThConfig
from binance_th.exceptions import BinanceThServerError
from binance_th.models.enums import RateLimitInterval, RateLimitType
from binance_th.ratelimit import DualWindowRateLimiter
from binance_th.retry import BackoffRetryer
from binance_th.timesync import TimeSync
from binance_th.transport import NullRateLimiter, NullRetryer, Transport

from .conftest import FakeTime, TransportFactory

_WEIGHT_MIN = (RateLimitType.REQUEST_WEIGHT, RateLimitInterval.MINUTE, 1)


def _json(
    payload: object, status: int = 200, headers: dict[str, str] | None = None
) -> httpx.Response:
    return httpx.Response(status, json=payload, headers=headers or {})


def _synced_ts(now: int = 1700000000000) -> TimeSync:
    ts = TimeSync(clock=lambda: now)
    ts.update(now)
    return ts


class TestRetryThroughTransport:
    """The retryer wraps the request pipeline."""

    async def test_read_5xx_retried_then_success(self, mock_transport: TransportFactory) -> None:
        """A read 5xx is retried after backoff and then succeeds."""
        calls = {"n": 0}

        def handler(_request: httpx.Request) -> httpx.Response:
            calls["n"] += 1
            if calls["n"] == 1:
                return httpx.Response(503, text="unavailable")
            return _json({"serverTime": 1700000000000})

        ft = FakeTime()
        transport, captured = mock_transport(
            handler, retryer=BackoffRetryer(jitter=lambda c: c, sleep=ft.sleep)
        )
        result = await transport.request("GET", "/api/v1/time", envelope=False)
        assert result == {"serverTime": 1700000000000}
        assert len(captured) == 2
        assert ft.sleeps == [0.5]

    async def test_mutating_5xx_not_retried(self, mock_transport: TransportFactory) -> None:
        """A 5xx on a mutating call is never auto-retried (deferred to M4)."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(503, text="unavailable")

        ft = FakeTime()
        cfg = BinanceThConfig(api_key="K", api_secret="S")
        transport, captured = mock_transport(
            handler, config=cfg, timesync=_synced_ts(), retryer=BackoffRetryer(sleep=ft.sleep)
        )
        with pytest.raises(BinanceThServerError):
            await transport.request("POST", "/api/v1/order", signed=True, mutating=True)
        assert len(captured) == 1
        assert ft.sleeps == []

    async def test_429_then_success_reconciles(self, mock_transport: TransportFactory) -> None:
        """A 429 honors Retry-After, retries, and the limiter reconciles from headers."""
        calls = {"n": 0}

        def handler(_request: httpx.Request) -> httpx.Response:
            calls["n"] += 1
            if calls["n"] == 1:
                return httpx.Response(
                    429,
                    json={"msg": "slow"},
                    headers={"Retry-After": "1", "x-mbx-used-weight-1m": "10"},
                )
            return _json({"serverTime": 1700000000000})

        ft = FakeTime()
        limiter = DualWindowRateLimiter.from_defaults(clock=ft.clock, sleep=ft.sleep)
        transport, captured = mock_transport(
            handler, limiter=limiter, retryer=BackoffRetryer(jitter=lambda c: c, sleep=ft.sleep)
        )
        result = await transport.request("GET", "/api/v1/time", envelope=False)
        assert result == {"serverTime": 1700000000000}
        assert len(captured) == 2
        assert ft.sleeps == [1.0]  # only the Retry-After sleep
        assert limiter._windows[_WEIGHT_MIN].used == 11  # reconciled to 10, then +1


class TestEngineGating:
    """Transport constructs real vs no-op engines from config."""

    async def test_limiter_gated_on_enable_rate_limiting(self) -> None:
        """Rate limiting is on by default and off when disabled."""
        on = Transport(BinanceThConfig())
        assert isinstance(on._limiter, DualWindowRateLimiter)
        await on.aclose()
        off = Transport(BinanceThConfig(enable_rate_limiting=False))
        assert isinstance(off._limiter, NullRateLimiter)
        await off.aclose()

    async def test_retryer_gated_on_max_retries(self) -> None:
        """A backoff retryer is used unless max_retries is 0."""
        on = Transport(BinanceThConfig())
        assert isinstance(on._retryer, BackoffRetryer)
        await on.aclose()
        off = Transport(BinanceThConfig(max_retries=0))
        assert isinstance(off._retryer, NullRetryer)
        await off.aclose()
