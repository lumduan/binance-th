"""Tests for enum definitions."""


from binance_th.models.enums import (
    DepositStatus,
    FilterType,
    KlineInterval,
    OrderSide,
    OrderStatus,
    OrderType,
    RateLimitInterval,
    RateLimitType,
    SymbolStatus,
    SymbolType,
    TimeInForce,
    WithdrawStatus,
)


class TestOrderSide:
    """Tests for OrderSide enum."""

    def test_buy_value(self) -> None:
        """Test BUY value."""
        assert OrderSide.BUY.value == "BUY"

    def test_sell_value(self) -> None:
        """Test SELL value."""
        assert OrderSide.SELL.value == "SELL"

    def test_string_conversion(self) -> None:
        """Test string conversion."""
        assert str(OrderSide.BUY) == "BUY"


class TestOrderType:
    """Tests for OrderType enum."""

    def test_all_order_types_defined(self) -> None:
        """Test all order types are defined."""
        expected_types = {
            "LIMIT",
            "MARKET",
            "STOP_LOSS",
            "STOP_LOSS_LIMIT",
            "TAKE_PROFIT",
            "TAKE_PROFIT_LIMIT",
            "LIMIT_MAKER",
        }
        actual_types = {t.value for t in OrderType}
        assert actual_types == expected_types

    def test_limit_value(self) -> None:
        """Test LIMIT value."""
        assert OrderType.LIMIT.value == "LIMIT"

    def test_market_value(self) -> None:
        """Test MARKET value."""
        assert OrderType.MARKET.value == "MARKET"


class TestOrderStatus:
    """Tests for OrderStatus enum."""

    def test_all_statuses_defined(self) -> None:
        """Test all order statuses are defined."""
        expected_statuses = {
            "NEW",
            "PARTIALLY_FILLED",
            "FILLED",
            "CANCELED",
            "REJECTED",
            "EXPIRED",
        }
        actual_statuses = {s.value for s in OrderStatus}
        assert actual_statuses == expected_statuses


class TestTimeInForce:
    """Tests for TimeInForce enum."""

    def test_gtc_value(self) -> None:
        """Test GTC value."""
        assert TimeInForce.GTC.value == "GTC"

    def test_ioc_value(self) -> None:
        """Test IOC value."""
        assert TimeInForce.IOC.value == "IOC"

    def test_fok_value(self) -> None:
        """Test FOK value."""
        assert TimeInForce.FOK.value == "FOK"


class TestKlineInterval:
    """Tests for KlineInterval enum."""

    def test_minute_intervals(self) -> None:
        """Test minute interval values."""
        assert KlineInterval.MINUTE_1.value == "1m"
        assert KlineInterval.MINUTE_5.value == "5m"
        assert KlineInterval.MINUTE_15.value == "15m"
        assert KlineInterval.MINUTE_30.value == "30m"

    def test_hour_intervals(self) -> None:
        """Test hour interval values."""
        assert KlineInterval.HOUR_1.value == "1h"
        assert KlineInterval.HOUR_4.value == "4h"
        assert KlineInterval.HOUR_12.value == "12h"

    def test_day_week_month_intervals(self) -> None:
        """Test day, week, month interval values."""
        assert KlineInterval.DAY_1.value == "1d"
        assert KlineInterval.WEEK_1.value == "1w"
        assert KlineInterval.MONTH_1.value == "1M"


class TestSymbolType:
    """Tests for SymbolType enum."""

    def test_global_value(self) -> None:
        """Test GLOBAL value."""
        assert SymbolType.GLOBAL.value == "GLOBAL"

    def test_site_value(self) -> None:
        """Test SITE value."""
        assert SymbolType.SITE.value == "SITE"


class TestSymbolStatus:
    """Tests for SymbolStatus enum."""

    def test_trading_value(self) -> None:
        """Test TRADING value."""
        assert SymbolStatus.TRADING.value == "TRADING"


class TestRateLimitType:
    """Tests for RateLimitType enum."""

    def test_all_rate_limit_types(self) -> None:
        """Test all rate limit types are defined."""
        expected = {"REQUEST_WEIGHT", "ORDERS", "RAW_REQUESTS"}
        actual = {t.value for t in RateLimitType}
        assert actual == expected


class TestRateLimitInterval:
    """Tests for RateLimitInterval enum."""

    def test_all_intervals(self) -> None:
        """Test all intervals are defined."""
        expected = {"SECOND", "MINUTE", "HOUR", "DAY"}
        actual = {i.value for i in RateLimitInterval}
        assert actual == expected


class TestFilterType:
    """Tests for FilterType enum."""

    def test_common_filters(self) -> None:
        """Test common filter types exist."""
        assert FilterType.PRICE_FILTER.value == "PRICE_FILTER"
        assert FilterType.LOT_SIZE.value == "LOT_SIZE"
        assert FilterType.MIN_NOTIONAL.value == "MIN_NOTIONAL"


class TestDepositStatus:
    """Tests for DepositStatus enum."""

    def test_pending_value(self) -> None:
        """Test PENDING value."""
        assert DepositStatus.PENDING.value == 0

    def test_success_value(self) -> None:
        """Test SUCCESS value."""
        assert DepositStatus.SUCCESS.value == 1

    def test_credited_value(self) -> None:
        """Test CREDITED value."""
        assert DepositStatus.CREDITED.value == 6


class TestWithdrawStatus:
    """Tests for WithdrawStatus enum."""

    def test_completed_value(self) -> None:
        """Test COMPLETED value."""
        assert WithdrawStatus.COMPLETED.value == 6

    def test_processing_value(self) -> None:
        """Test PROCESSING value."""
        assert WithdrawStatus.PROCESSING.value == 4
