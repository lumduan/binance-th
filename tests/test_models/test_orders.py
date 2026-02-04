"""Tests for order models."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from binance_th.models.enums import OrderSide, OrderStatus, OrderType, TimeInForce
from binance_th.models.orders import (
    CancelOrderRequest,
    Order,
    OrderRequest,
    QueryOrderRequest,
)


class TestOrder:
    """Tests for Order response model."""

    def test_order_parsing(self) -> None:
        """Test parsing order response."""
        data = {
            "symbol": "BTCUSDT",
            "orderId": 12345,
            "orderListId": -1,
            "clientOrderId": "my_order_123",
            "price": "50000.00",
            "origQty": "1.0",
            "executedQty": "0.5",
            "cummulativeQuoteQty": "25000.00",
            "status": "PARTIALLY_FILLED",
            "timeInForce": "GTC",
            "type": "LIMIT",
            "side": "BUY",
            "time": 1234567890000,
            "updateTime": 1234567890100,
            "isWorking": True,
            "origQuoteOrderQty": "0.0",
        }
        order = Order(**data)
        assert order.symbol == "BTCUSDT"
        assert order.order_id == 12345
        assert order.price == Decimal("50000.00")
        assert order.status == OrderStatus.PARTIALLY_FILLED
        assert order.order_type == OrderType.LIMIT
        assert order.side == OrderSide.BUY

    def test_is_filled_property(self) -> None:
        """Test is_filled property."""
        data = {
            "symbol": "BTCUSDT",
            "orderId": 12345,
            "clientOrderId": "my_order",
            "price": "50000.00",
            "origQty": "1.0",
            "executedQty": "1.0",
            "cummulativeQuoteQty": "50000.00",
            "status": "FILLED",
            "timeInForce": "GTC",
            "type": "LIMIT",
            "side": "BUY",
            "time": 1234567890000,
            "updateTime": 1234567890100,
            "isWorking": False,
            "origQuoteOrderQty": "0.0",
        }
        order = Order(**data)
        assert order.is_filled is True

    def test_is_active_property(self) -> None:
        """Test is_active property."""
        data = {
            "symbol": "BTCUSDT",
            "orderId": 12345,
            "clientOrderId": "my_order",
            "price": "50000.00",
            "origQty": "1.0",
            "executedQty": "0.0",
            "cummulativeQuoteQty": "0.0",
            "status": "NEW",
            "timeInForce": "GTC",
            "type": "LIMIT",
            "side": "BUY",
            "time": 1234567890000,
            "updateTime": 1234567890000,
            "isWorking": True,
            "origQuoteOrderQty": "0.0",
        }
        order = Order(**data)
        assert order.is_active is True

    def test_filled_percent_property(self) -> None:
        """Test filled_percent property."""
        data = {
            "symbol": "BTCUSDT",
            "orderId": 12345,
            "clientOrderId": "my_order",
            "price": "50000.00",
            "origQty": "1.0",
            "executedQty": "0.5",
            "cummulativeQuoteQty": "25000.00",
            "status": "PARTIALLY_FILLED",
            "timeInForce": "GTC",
            "type": "LIMIT",
            "side": "BUY",
            "time": 1234567890000,
            "updateTime": 1234567890100,
            "isWorking": True,
            "origQuoteOrderQty": "0.0",
        }
        order = Order(**data)
        assert order.filled_percent == Decimal("50")


class TestOrderRequest:
    """Tests for OrderRequest model."""

    def test_valid_limit_order(self) -> None:
        """Test valid LIMIT order request."""
        request = OrderRequest(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("0.001"),
            price=Decimal("50000"),
            time_in_force=TimeInForce.GTC,
        )
        assert request.symbol == "BTCUSDT"
        assert request.side == OrderSide.BUY
        assert request.order_type == OrderType.LIMIT

    def test_limit_order_requires_price(self) -> None:
        """Test that LIMIT order requires price."""
        with pytest.raises(ValidationError) as exc_info:
            OrderRequest(
                symbol="BTCUSDT",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                quantity=Decimal("0.001"),
                time_in_force=TimeInForce.GTC,
            )
        assert "price is required for LIMIT orders" in str(exc_info.value)

    def test_limit_order_requires_time_in_force(self) -> None:
        """Test that LIMIT order requires timeInForce."""
        with pytest.raises(ValidationError) as exc_info:
            OrderRequest(
                symbol="BTCUSDT",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                quantity=Decimal("0.001"),
                price=Decimal("50000"),
            )
        assert "timeInForce is required for LIMIT orders" in str(exc_info.value)

    def test_limit_order_requires_quantity(self) -> None:
        """Test that LIMIT order requires quantity."""
        with pytest.raises(ValidationError) as exc_info:
            OrderRequest(
                symbol="BTCUSDT",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                price=Decimal("50000"),
                time_in_force=TimeInForce.GTC,
            )
        assert "quantity is required for LIMIT orders" in str(exc_info.value)

    def test_valid_market_order_with_quantity(self) -> None:
        """Test valid MARKET order with quantity."""
        request = OrderRequest(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("0.001"),
        )
        assert request.order_type == OrderType.MARKET
        assert request.quantity == Decimal("0.001")

    def test_valid_market_order_with_quote_qty(self) -> None:
        """Test valid MARKET order with quoteOrderQty."""
        request = OrderRequest(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quote_order_qty=Decimal("100"),
        )
        assert request.quote_order_qty == Decimal("100")

    def test_market_order_requires_quantity_or_quote(self) -> None:
        """Test that MARKET order requires quantity or quoteOrderQty."""
        with pytest.raises(ValidationError) as exc_info:
            OrderRequest(
                symbol="BTCUSDT",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
            )
        assert "Either quantity or quoteOrderQty is required" in str(exc_info.value)

    def test_stop_loss_requires_stop_price(self) -> None:
        """Test that STOP_LOSS order requires stopPrice."""
        with pytest.raises(ValidationError) as exc_info:
            OrderRequest(
                symbol="BTCUSDT",
                side=OrderSide.SELL,
                order_type=OrderType.STOP_LOSS,
                quantity=Decimal("0.001"),
            )
        assert "stopPrice is required for STOP orders" in str(exc_info.value)

    def test_valid_stop_loss_limit_order(self) -> None:
        """Test valid STOP_LOSS_LIMIT order."""
        request = OrderRequest(
            symbol="BTCUSDT",
            side=OrderSide.SELL,
            order_type=OrderType.STOP_LOSS_LIMIT,
            quantity=Decimal("0.001"),
            price=Decimal("49000"),
            stop_price=Decimal("49500"),
            time_in_force=TimeInForce.GTC,
        )
        assert request.stop_price == Decimal("49500")

    def test_recv_window_max_value(self) -> None:
        """Test recvWindow maximum value validation."""
        with pytest.raises(ValidationError):
            OrderRequest(
                symbol="BTCUSDT",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=Decimal("0.001"),
                recv_window=70000,  # Exceeds max of 60000
            )


class TestCancelOrderRequest:
    """Tests for CancelOrderRequest model."""

    def test_valid_with_order_id(self) -> None:
        """Test valid request with orderId."""
        request = CancelOrderRequest(symbol="BTCUSDT", order_id=12345)
        assert request.order_id == 12345

    def test_valid_with_client_order_id(self) -> None:
        """Test valid request with origClientOrderId."""
        request = CancelOrderRequest(symbol="BTCUSDT", orig_client_order_id="my_order")
        assert request.orig_client_order_id == "my_order"

    def test_requires_identifier(self) -> None:
        """Test that either orderId or origClientOrderId is required."""
        with pytest.raises(ValidationError) as exc_info:
            CancelOrderRequest(symbol="BTCUSDT")
        assert "Either orderId or origClientOrderId is required" in str(exc_info.value)


class TestQueryOrderRequest:
    """Tests for QueryOrderRequest model."""

    def test_valid_with_order_id(self) -> None:
        """Test valid request with orderId."""
        request = QueryOrderRequest(symbol="BTCUSDT", order_id=12345)
        assert request.order_id == 12345

    def test_valid_with_client_order_id(self) -> None:
        """Test valid request with origClientOrderId."""
        request = QueryOrderRequest(symbol="BTCUSDT", orig_client_order_id="my_order")
        assert request.orig_client_order_id == "my_order"

    def test_requires_identifier(self) -> None:
        """Test that either orderId or origClientOrderId is required."""
        with pytest.raises(ValidationError) as exc_info:
            QueryOrderRequest(symbol="BTCUSDT")
        assert "Either orderId or origClientOrderId is required" in str(exc_info.value)
