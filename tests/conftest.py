"""Pytest configuration and fixtures for Binance Thailand library tests."""

from collections.abc import AsyncIterator, Callable

import httpx
import pytest

from binance_th.config import BinanceThConfig
from binance_th.timesync import TimeSync
from binance_th.transport import (
    NullRateLimiter,
    NullRetryer,
    RateLimiter,
    Retryer,
    Transport,
)

Handler = Callable[[httpx.Request], httpx.Response]
TransportFactory = Callable[..., tuple[Transport, list[httpx.Request]]]


class FakeTime:
    """Controllable monotonic clock + recording async sleep for deterministic timing tests."""

    def __init__(self, start: float = 1000.0) -> None:
        self.now = start
        self.sleeps: list[float] = []

    def clock(self) -> float:
        return self.now

    async def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


@pytest.fixture
def config() -> BinanceThConfig:
    """Create test configuration."""
    return BinanceThConfig(
        api_key="test_api_key",
        api_secret="test_api_secret",
    )


@pytest.fixture
def config_no_auth() -> BinanceThConfig:
    """Create test configuration without authentication."""
    return BinanceThConfig()


@pytest.fixture
async def mock_transport() -> AsyncIterator[TransportFactory]:
    """Factory building a Transport backed by ``httpx.MockTransport``.

    Returns ``(transport, captured)`` where ``captured`` is a list of the
    outgoing ``httpx.Request`` objects, so tests can assert on signed params and
    headers. Created transports are closed on teardown.
    """
    created: list[Transport] = []

    def _make(
        handler: Handler,
        *,
        config: BinanceThConfig | None = None,
        timesync: TimeSync | None = None,
        limiter: RateLimiter | None = None,
        retryer: Retryer | None = None,
    ) -> tuple[Transport, list[httpx.Request]]:
        captured: list[httpx.Request] = []

        def wrapped(request: httpx.Request) -> httpx.Response:
            captured.append(request)
            return handler(request)

        cfg = config or BinanceThConfig(api_key="test_key", api_secret="test_secret")
        client = httpx.AsyncClient(
            transport=httpx.MockTransport(wrapped), base_url=cfg.rest_base_url
        )
        # Default to no-op engines so unrelated tests stay hermetic and fast; M2
        # tests opt into real engines with a FakeTime sleep.
        transport = Transport(
            cfg,
            client=client,
            timesync=timesync,
            limiter=limiter or NullRateLimiter(),
            retryer=retryer or NullRetryer(),
        )
        created.append(transport)
        return transport, captured

    yield _make
    for transport in created:
        await transport.aclose()
