"""Tests for BinanceThClient (ADR-0015)."""

import warnings

import httpx

from binance_th import BinanceThClient
from binance_th.config import BinanceThConfig
from binance_th.models.enums import RateLimitInterval, RateLimitType, SymbolType
from binance_th.ratelimit import DualWindowRateLimiter
from binance_th.stream import StreamClient
from binance_th.userstream import UserDataStream

from .conftest import TransportFactory


def _exchange_info_body(*, weight_limit: int = 6000) -> dict[str, object]:
    """A trimmed real exchangeInfo body (one SITE symbol)."""
    return {
        "timezone": "UTC",
        "serverTime": 1700000000000,
        "rateLimits": [
            {
                "rateLimitType": "REQUEST_WEIGHT",
                "interval": "MINUTE",
                "intervalNum": 1,
                "limit": weight_limit,
            }
        ],
        "exchangeFilters": [],
        "symbols": [
            {
                "symbol": "BNBTHB",
                "test": 0,
                "status": "TRADING",
                "baseAsset": "BNB",
                "baseAssetPrecision": 8,
                "quoteAsset": "THB",
                "quotePrecision": 6,
                "quoteAssetPrecision": 8,
                "baseCommissionPrecision": 2,
                "quoteCommissionPrecision": 0,
                "type": "SITE",
                "filters": [
                    {
                        "filterType": "PRICE_FILTER",
                        "minPrice": "0.01",
                        "maxPrice": "1000000.0",
                        "tickSize": "0.01",
                    }
                ],
                "orderTypes": ["LIMIT", "MARKET"],
            }
        ],
    }


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

    async def test_ws_client_attached_and_torn_down(self, mock_transport: TransportFactory) -> None:
        """The client exposes a StreamClient at ``.ws`` and closes it on aclose (ADR-0015)."""

        def handler(_request: httpx.Request) -> httpx.Response:  # pragma: no cover - unused
            return httpx.Response(200, text="pong")

        transport, _ = mock_transport(handler)
        client = BinanceThClient(transport=transport)
        assert isinstance(client.ws, StreamClient)
        await client.aclose()
        assert client.ws._closing is True
        assert client.is_closed is True

    async def test_user_stream_attached_and_torn_down(
        self, mock_transport: TransportFactory
    ) -> None:
        """The client exposes a UserDataStream at ``.user_stream`` and closes it (ADR-0008)."""

        def handler(_request: httpx.Request) -> httpx.Response:  # pragma: no cover - unused
            return httpx.Response(200, text="pong")

        transport, captured = mock_transport(handler)
        client = BinanceThClient(transport=transport)
        assert isinstance(client.user_stream, UserDataStream)
        await client.aclose()
        assert client.user_stream._closing is True
        assert captured == []  # never started -> no listenKey POST/DELETE
        assert client.is_closed is True


class TestExchangeInfoAndSymbolTypes:
    """exchangeInfo caching + limiter reseed, and symbolType (M3a)."""

    async def test_parses_and_caches(self, mock_transport: TransportFactory) -> None:
        """exchange_info parses the live shape and caches (one HTTP call)."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json=_exchange_info_body())

        transport, captured = mock_transport(handler)
        client = BinanceThClient(transport=transport)
        first = await client.exchange_info()
        second = await client.exchange_info()
        assert first is second
        assert len(captured) == 1
        symbol = first.get_symbol("BNBTHB")
        assert symbol is not None
        assert symbol.symbol_type == SymbolType.SITE

    async def test_force_refetches(self, mock_transport: TransportFactory) -> None:
        """force=True re-fetches."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json=_exchange_info_body())

        transport, captured = mock_transport(handler)
        client = BinanceThClient(transport=transport)
        await client.exchange_info()
        await client.exchange_info(force=True)
        assert len(captured) == 2

    async def test_reseeds_limiter(self, mock_transport: TransportFactory) -> None:
        """The limiter adopts the exchangeInfo rate limits."""
        limiter = DualWindowRateLimiter.from_defaults()

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json=_exchange_info_body(weight_limit=12000))

        transport, _ = mock_transport(handler, limiter=limiter)
        await BinanceThClient(transport=transport).exchange_info()
        window = limiter._windows[(RateLimitType.REQUEST_WEIGHT, RateLimitInterval.MINUTE, 1)]
        assert window.limit == 12000

    async def test_null_limiter_reseed_noop(self, mock_transport: TransportFactory) -> None:
        """With the default NullRateLimiter, reseed is a harmless no-op."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json=_exchange_info_body())

        transport, _ = mock_transport(handler)  # NullRateLimiter default
        info = await BinanceThClient(transport=transport).exchange_info()
        assert info.timezone == "UTC"

    async def test_symbol_types(self, mock_transport: TransportFactory) -> None:
        """symbol_types returns a list; the symbol filter is forwarded when given."""

        def handler(request: httpx.Request) -> httpx.Response:
            if "symbol" in request.url.params:
                assert request.url.params["symbol"] == "BNBTHB"
                return httpx.Response(200, json=[{"symbol": "BNBTHB", "type": "SITE"}])
            return httpx.Response(
                200,
                json=[
                    {"symbol": "BNBTHB", "type": "SITE"},
                    {"symbol": "BTCUSDT", "type": "GLOBAL"},
                ],
            )

        client = BinanceThClient(transport=mock_transport(handler)[0])
        types = await client.symbol_types()
        assert len(types) == 2
        assert types[0].symbol_type == SymbolType.SITE
        one = await client.symbol_types(symbol="BNBTHB")
        assert len(one) == 1 and one[0].symbol == "BNBTHB"
