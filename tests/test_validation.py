"""Tests for pre-trade validation (ADR-0009)."""

from decimal import Decimal

import pytest

from binance_th.exceptions import BinanceThValidationError
from binance_th.models.base import SymbolInfo
from binance_th.models.enums import OrderSide, OrderType, TimeInForce
from binance_th.models.orders import OrderRequest
from binance_th.validation import snap_price, snap_qty, validate_order


def _symbol(
    *,
    tick: str = "0.01",
    step: str = "0.001",
    min_qty: str = "0",
    max_qty: str = "0",
    min_notional: str = "0",
    min_price: str = "0",
    max_price: str = "0",
) -> SymbolInfo:
    return SymbolInfo(
        symbol="BTCTHB",
        status="TRADING",
        baseAsset="BTC",
        baseAssetPrecision=8,
        quoteAsset="THB",
        quotePrecision=2,
        quoteAssetPrecision=8,
        orderTypes=["LIMIT", "MARKET"],
        filters=[
            {
                "filterType": "PRICE_FILTER",
                "minPrice": min_price,
                "maxPrice": max_price,
                "tickSize": tick,
            },
            {"filterType": "LOT_SIZE", "minQty": min_qty, "maxQty": max_qty, "stepSize": step},
            {"filterType": "MIN_NOTIONAL", "minNotional": min_notional, "applyToMarket": True},
        ],
    )


def _limit(price: str = "50000", qty: str = "0.001") -> OrderRequest:
    return OrderRequest(
        symbol="BTCTHB",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        price=Decimal(price),
        quantity=Decimal(qty),
        time_in_force=TimeInForce.GTC,
    )


class TestSnap:
    """Floor-division snapping (not quantize)."""

    def test_snap_price_non_power_of_ten_tick(self) -> None:
        assert snap_price(Decimal("1.07"), Decimal("0.05")) == Decimal("1.05")

    def test_snap_price_multiple(self) -> None:
        assert snap_price(Decimal("0.0037"), Decimal("0.001")) == Decimal("0.003")

    def test_snap_zero_or_none_unchanged(self) -> None:
        assert snap_price(Decimal("1.234"), Decimal("0")) == Decimal("1.234")
        assert snap_price(Decimal("1.234"), None) == Decimal("1.234")

    def test_snap_qty(self) -> None:
        assert snap_qty(Decimal("1.2345"), Decimal("0.001")) == Decimal("1.234")


class TestValidateOrder:
    """Snapping + bound/notional enforcement."""

    def test_snaps_price_and_qty(self) -> None:
        out = validate_order(_limit(price="50000.037", qty="0.0019"), _symbol())
        assert out.price == Decimal("50000.03")
        assert out.quantity == Decimal("0.001")

    def test_zero_tick_no_snap(self) -> None:
        out = validate_order(_limit(price="50000.037", qty="1"), _symbol(tick="0.0", step="0.0"))
        assert out.price == Decimal("50000.037")

    def test_sub_min_notional_raises(self) -> None:
        with pytest.raises(BinanceThValidationError) as exc:
            validate_order(_limit(price="1", qty="0.001"), _symbol(min_notional="10"))
        assert exc.value.field == "notional"

    def test_qty_below_min_raises(self) -> None:
        with pytest.raises(BinanceThValidationError) as exc:
            validate_order(_limit(price="50000", qty="0.005"), _symbol(min_qty="0.01"))
        assert exc.value.field == "quantity"

    def test_qty_snapped_to_zero_raises(self) -> None:
        with pytest.raises(BinanceThValidationError) as exc:
            validate_order(_limit(price="50000", qty="0.0005"), _symbol(step="0.001"))
        assert exc.value.field == "quantity"

    def test_qty_above_max_raises(self) -> None:
        with pytest.raises(BinanceThValidationError) as exc:
            validate_order(_limit(price="50000", qty="5"), _symbol(max_qty="1"))
        assert exc.value.field == "quantity"

    def test_market_by_quote_qty_notional(self) -> None:
        request = OrderRequest(
            symbol="BTCTHB",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quote_order_qty=Decimal("5"),
        )
        with pytest.raises(BinanceThValidationError) as exc:
            validate_order(request, _symbol(min_notional="10"))
        assert exc.value.field == "notional"

    def test_conforming_order_passes(self) -> None:
        out = validate_order(_limit(price="50000", qty="0.001"), _symbol())
        assert out.price == Decimal("50000")
        assert out.quantity == Decimal("0.001")

    def test_price_zero_raises(self) -> None:
        with pytest.raises(BinanceThValidationError) as exc:
            validate_order(_limit(price="0"), _symbol())
        assert exc.value.field == "price"

    def test_price_below_min_raises(self) -> None:
        with pytest.raises(BinanceThValidationError) as exc:
            validate_order(_limit(price="50000"), _symbol(min_price="60000"))
        assert exc.value.field == "price"

    def test_price_above_max_raises(self) -> None:
        with pytest.raises(BinanceThValidationError) as exc:
            validate_order(_limit(price="50000"), _symbol(max_price="40000"))
        assert exc.value.field == "price"

    def test_stop_order_snaps_stop_price(self) -> None:
        stop = OrderRequest(
            symbol="BTCTHB",
            side=OrderSide.SELL,
            order_type=OrderType.STOP_LOSS_LIMIT,
            price=Decimal("49000"),
            stop_price=Decimal("49500.037"),
            quantity=Decimal("0.001"),
            time_in_force=TimeInForce.GTC,
        )
        out = validate_order(stop, _symbol(tick="0.01"))
        assert out.stop_price == Decimal("49500.03")

    def test_market_quote_qty_no_snap_returns_same(self) -> None:
        request = OrderRequest(
            symbol="BTCTHB",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quote_order_qty=Decimal("100"),
        )
        out = validate_order(request, _symbol())
        assert out is request  # nothing snapped → same object returned
