"""Tests for the signed OrdersClient (M4). Mock-only — orders place real money."""

import hashlib
import hmac
from decimal import Decimal

import httpx
import pytest

from binance_th.config import BinanceThConfig
from binance_th.exceptions import (
    BinanceThAuthError,
    BinanceThOrderUnknownError,
    BinanceThValidationError,
)
from binance_th.models.base import ExchangeInfo
from binance_th.models.orders import Order, OrderRequest
from binance_th.orders import OrdersClient
from binance_th.timesync import TimeSync

from .conftest import Handler, TransportFactory

_SYMBOL = {
    "symbol": "BTCTHB",
    "status": "TRADING",
    "baseAsset": "BTC",
    "baseAssetPrecision": 8,
    "quoteAsset": "THB",
    "quotePrecision": 2,
    "quoteAssetPrecision": 8,
    "type": "SITE",
    "orderTypes": ["LIMIT", "MARKET"],
    "filters": [
        {"filterType": "PRICE_FILTER", "minPrice": "0", "maxPrice": "0", "tickSize": "0.01"},
        {"filterType": "LOT_SIZE", "minQty": "0", "maxQty": "0", "stepSize": "0.001"},
        {"filterType": "MIN_NOTIONAL", "minNotional": "0", "applyToMarket": True},
    ],
}

_ORDER_RESPONSE = {
    "symbol": "BTCTHB",
    "orderId": 1,
    "orderListId": -1,
    "clientOrderId": "x-test-1",
    "price": "50000.03",
    "origQty": "0.001",
    "executedQty": "0",
    "cummulativeQuoteQty": "0",
    "status": "NEW",
    "timeInForce": "GTC",
    "type": "LIMIT",
    "side": "BUY",
    "time": 1,
    "updateTime": 1,
    "isWorking": True,
    "origQuoteOrderQty": "0",
}


def _synced_ts(now: int = 1700000000000) -> TimeSync:
    ts = TimeSync(clock=lambda: now)
    ts.update(now)
    return ts


def _exchange_info(symbols: list[dict[str, object]] | None = None) -> ExchangeInfo:
    return ExchangeInfo(
        timezone="UTC",
        serverTime=1,
        rateLimits=[],
        exchangeFilters=[],
        symbols=[_SYMBOL] if symbols is None else symbols,
    )


def _orders(
    mock_transport: TransportFactory,
    handler: Handler,
    *,
    config: BinanceThConfig | None = None,
    provider: object = None,
    coid: str = "x-test-1",
) -> tuple[OrdersClient, list[httpx.Request]]:
    cfg = config or BinanceThConfig(api_key="KEY", api_secret="SECRET")
    transport, captured = mock_transport(handler, config=cfg, timesync=_synced_ts())

    async def default_provider(**_kwargs: object) -> ExchangeInfo:
        return _exchange_info()

    client = OrdersClient(
        transport, exchange_info=provider or default_provider, client_order_id_factory=lambda: coid
    )
    return client, captured


class TestCreateOrder:
    """create_order: signing, minting, snapping."""

    async def test_limit_signed_snapped_and_minted(self, mock_transport: TransportFactory) -> None:
        """Kwargs build a signed order with snapped price/qty and a minted client id."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json=_ORDER_RESPONSE)

        orders, captured = _orders(mock_transport, handler, coid="x-test-1")
        order = await orders.create_order(
            "BTCTHB",
            "BUY",
            "LIMIT",
            price=Decimal("50000.037"),
            quantity=Decimal("0.0019"),
            time_in_force="GTC",
        )
        assert isinstance(order, Order)
        assert order.client_order_id == "x-test-1"

        request = captured[-1]
        assert request.method == "POST"
        assert request.headers["X-MBX-APIKEY"] == "KEY"
        query = request.url.query.decode()
        assert "price=50000.03" in query  # snapped to tickSize
        assert "quantity=0.001" in query  # snapped to stepSize
        assert "newClientOrderId=x-test-1" in query
        # signature is last and covers exactly the sent params (URL-safe → sign==send)
        parts = query.split("&")
        assert parts[-1].startswith("signature=")
        expected = hmac.new(b"SECRET", "&".join(parts[:-1]).encode(), hashlib.sha256).hexdigest()
        assert parts[-1] == f"signature={expected}"

    async def test_accepts_prebuilt_request(self, mock_transport: TransportFactory) -> None:
        """A pre-built OrderRequest is sent as-is (minus minting)."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json=_ORDER_RESPONSE)

        orders, captured = _orders(mock_transport, handler)
        req = OrderRequest(
            symbol="BTCTHB",
            side="BUY",
            order_type="LIMIT",
            price=Decimal("50000"),
            quantity=Decimal("0.001"),
            time_in_force="GTC",
        )
        await orders.create_order(request=req, validate=False)
        assert captured[-1].method == "POST"

    async def test_request_and_kwargs_conflict(self, mock_transport: TransportFactory) -> None:
        """Passing both request= and kwargs is a ValueError, no HTTP."""

        def handler(_request: httpx.Request) -> httpx.Response:  # pragma: no cover - never called
            return httpx.Response(200, json=_ORDER_RESPONSE)

        orders, captured = _orders(mock_transport, handler)
        req = OrderRequest(symbol="BTCTHB", side="BUY", order_type="MARKET", quantity=Decimal("1"))
        with pytest.raises(ValueError, match="either request"):
            await orders.create_order("BTCTHB", request=req)
        assert captured == []

    async def test_validate_false_skips_provider(self, mock_transport: TransportFactory) -> None:
        """validate=False never calls the exchange_info provider."""

        async def boom(**_kwargs: object) -> ExchangeInfo:  # pragma: no cover - must not run
            raise AssertionError("provider should not be called")

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json=_ORDER_RESPONSE)

        orders, _ = _orders(mock_transport, handler, provider=boom)
        order = await orders.create_order(
            "BTCTHB",
            "BUY",
            "LIMIT",
            price=Decimal("50000"),
            quantity=Decimal("0.001"),
            time_in_force="GTC",
            validate=False,
        )
        assert order.order_id == 1

    async def test_unknown_symbol_raises_before_post(
        self, mock_transport: TransportFactory
    ) -> None:
        """An unknown symbol force-refreshes then raises, with no POST."""
        calls = {"n": 0}

        async def provider(**_kwargs: object) -> ExchangeInfo:
            calls["n"] += 1
            return _exchange_info(symbols=[])

        def handler(_request: httpx.Request) -> httpx.Response:  # pragma: no cover - never called
            return httpx.Response(200, json=_ORDER_RESPONSE)

        orders, captured = _orders(mock_transport, handler, provider=provider)
        with pytest.raises(BinanceThValidationError) as exc:
            await orders.create_order(
                "NOPE",
                "BUY",
                "LIMIT",
                price=Decimal("1"),
                quantity=Decimal("1"),
                time_in_force="GTC",
            )
        assert exc.value.field == "symbol"
        assert calls["n"] == 2  # normal + force refresh
        assert captured == []

    async def test_missing_credentials_raises(self, mock_transport: TransportFactory) -> None:
        """A signed create without credentials raises before any network hit."""

        def handler(_request: httpx.Request) -> httpx.Response:  # pragma: no cover - never called
            return httpx.Response(200, json=_ORDER_RESPONSE)

        orders, captured = _orders(mock_transport, handler, config=BinanceThConfig())
        with pytest.raises(BinanceThAuthError):
            await orders.create_order(
                "BTCTHB", "BUY", "MARKET", quantity=Decimal("1"), validate=False
            )
        assert captured == []


class TestUnknownReconciliation:
    """5xx-UNKNOWN reconciliation (ADR-0006) — the safety crux."""

    async def test_reconcile_found_no_second_post(self, mock_transport: TransportFactory) -> None:
        """POST 503 → query by client id finds the order → returned; no second POST."""
        calls = {"post": 0, "get": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            if request.method == "POST":
                calls["post"] += 1
                return httpx.Response(503, text="unavailable")
            calls["get"] += 1
            return httpx.Response(200, json=_ORDER_RESPONSE)

        orders, captured = _orders(mock_transport, handler, coid="x-test-1")
        order = await orders.create_order(
            "BTCTHB",
            "BUY",
            "LIMIT",
            price=Decimal("50000"),
            quantity=Decimal("0.001"),
            time_in_force="GTC",
            validate=False,
        )
        assert order.client_order_id == "x-test-1"
        assert calls == {"post": 1, "get": 1}
        get_request = next(c for c in reversed(captured) if c.method == "GET")
        assert "origClientOrderId=x-test-1" in get_request.url.query.decode()

    async def test_reconcile_not_found_resubmittable(
        self, mock_transport: TransportFactory
    ) -> None:
        """POST 503 → query says -2013 (not placed) → UNKNOWN(resubmittable=True)."""

        def handler(request: httpx.Request) -> httpx.Response:
            if request.method == "POST":
                return httpx.Response(503, text="down")
            return httpx.Response(400, json={"code": -2013, "msg": "Order does not exist."})

        orders, _ = _orders(mock_transport, handler, coid="x-test-1")
        with pytest.raises(BinanceThOrderUnknownError) as exc:
            await orders.create_order(
                "BTCTHB",
                "BUY",
                "LIMIT",
                price=Decimal("50000"),
                quantity=Decimal("0.001"),
                time_in_force="GTC",
                validate=False,
            )
        assert exc.value.resubmittable is True
        assert exc.value.client_order_id == "x-test-1"

    async def test_reconcile_query_fails_not_resubmittable(
        self, mock_transport: TransportFactory
    ) -> None:
        """POST 503 → reconciliation query also fails → UNKNOWN(resubmittable=False)."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(503, text="down")

        orders, _ = _orders(mock_transport, handler, coid="x-test-1")
        with pytest.raises(BinanceThOrderUnknownError) as exc:
            await orders.create_order(
                "BTCTHB",
                "BUY",
                "LIMIT",
                price=Decimal("50000"),
                quantity=Decimal("0.001"),
                time_in_force="GTC",
                validate=False,
            )
        assert exc.value.resubmittable is False


class TestCancelQueryOpen:
    """cancel / query / openOrders."""

    async def test_cancel_by_order_id(self, mock_transport: TransportFactory) -> None:
        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={**_ORDER_RESPONSE, "status": "CANCELED"})

        orders, captured = _orders(mock_transport, handler)
        order = await orders.cancel_order("BTCTHB", order_id=1)
        assert order.symbol == "BTCTHB"
        assert captured[-1].method == "DELETE"
        assert "orderId=1" in captured[-1].url.query.decode()

    async def test_cancel_requires_identifier(self, mock_transport: TransportFactory) -> None:
        def handler(_request: httpx.Request) -> httpx.Response:  # pragma: no cover - never called
            return httpx.Response(200, json=_ORDER_RESPONSE)

        orders, captured = _orders(mock_transport, handler)
        with pytest.raises(ValueError, match="orderId or origClientOrderId"):
            await orders.cancel_order("BTCTHB")
        assert captured == []

    async def test_query_by_client_id(self, mock_transport: TransportFactory) -> None:
        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json=_ORDER_RESPONSE)

        orders, captured = _orders(mock_transport, handler)
        order = await orders.query_order("BTCTHB", orig_client_order_id="x-test-1")
        assert order.client_order_id == "x-test-1"
        assert captured[-1].method == "GET"

    async def test_open_orders(self, mock_transport: TransportFactory) -> None:
        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json=[_ORDER_RESPONSE, {**_ORDER_RESPONSE, "orderId": 2}])

        orders, captured = _orders(mock_transport, handler)
        result = await orders.open_orders("BTCTHB")
        assert len(result) == 2
        assert "symbol=BTCTHB" in captured[-1].url.query.decode()
