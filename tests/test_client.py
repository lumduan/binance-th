"""Tests for BinanceThClient (ADR-0015)."""

import warnings

import httpx

from binance_th import BinanceThClient
from binance_th.config import BinanceThConfig

from .conftest import TransportFactory


class TestBinanceThClient:
    """Tests for the public async client."""

    async def test_ping_true(self, mock_transport: TransportFactory) -> None:
        """ping returns True when the API answers `pong`."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, text="pong")

        transport, _ = mock_transport(handler)
        client = BinanceThClient(transport=transport)
        assert await client.ping() is True

    async def test_server_time(self, mock_transport: TransportFactory) -> None:
        """server_time delegates to the transport and returns a ServerTime."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"serverTime": 1700000000000})

        transport, _ = mock_transport(handler)
        client = BinanceThClient(transport=transport)
        server_time = await client.server_time()
        assert server_time.server_time == 1700000000000

    async def test_context_manager_closes(self, mock_transport: TransportFactory) -> None:
        """The context manager closes the transport on exit."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, text="pong")

        transport, _ = mock_transport(handler)
        client = BinanceThClient(transport=transport)
        async with client as entered:
            assert entered.is_closed is False
            await entered.ping()
        assert client.is_closed is True

    async def test_aclose_idempotent(self, mock_transport: TransportFactory) -> None:
        """Closing twice is safe."""

        def handler(_request: httpx.Request) -> httpx.Response:  # pragma: no cover - unused
            return httpx.Response(200, text="pong")

        transport, _ = mock_transport(handler)
        client = BinanceThClient(transport=transport)
        await client.aclose()
        await client.aclose()
        assert client.is_closed is True

    async def test_real_client_closes_without_warning(self) -> None:
        """A real (non-mocked) client opens and closes with no ResourceWarning."""
        with warnings.catch_warnings():
            warnings.simplefilter("error", ResourceWarning)
            async with BinanceThClient(BinanceThConfig()) as client:
                assert client.is_closed is False
            assert client.is_closed is True
