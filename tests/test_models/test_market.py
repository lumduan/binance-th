"""Tests for market data models."""

from decimal import Decimal

from binance_th.models.market import (
    AggregateTrade,
    BookTicker,
    Kline,
    OrderBook,
    OrderBookEntry,
    PriceTicker,
    Ticker24hr,
    Trade,
)


class TestOrderBookEntry:
    """Tests for OrderBookEntry model."""

    def test_from_list(self) -> None:
        """Test creating entry from list format."""
        entry = OrderBookEntry.from_list(["50000.00", "0.5"])
        assert entry.price == Decimal("50000.00")
        assert entry.quantity == Decimal("0.5")

    def test_direct_creation(self) -> None:
        """Test direct model creation."""
        entry = OrderBookEntry(price=Decimal("50000"), quantity=Decimal("1.5"))
        assert entry.price == Decimal("50000")
        assert entry.quantity == Decimal("1.5")


class TestOrderBook:
    """Tests for OrderBook model."""

    def test_from_api(self) -> None:
        """Test creating from API response format."""
        data = {
            "lastUpdateId": 123456789,
            "bids": [["50000.00", "1.0"], ["49999.00", "2.0"]],
            "asks": [["50001.00", "0.5"], ["50002.00", "1.5"]],
        }
        order_book = OrderBook.from_api(data)
        assert order_book.last_update_id == 123456789
        assert len(order_book.bids) == 2
        assert len(order_book.asks) == 2
        assert order_book.bids[0].price == Decimal("50000.00")
        assert order_book.asks[0].price == Decimal("50001.00")


class TestTrade:
    """Tests for Trade model."""

    def test_trade_parsing(self) -> None:
        """Test parsing trade data."""
        data = {
            "id": 123,
            "price": "50000.00",
            "qty": "0.001",
            "quoteQty": "50.00",
            "time": 1234567890000,
            "isBuyerMaker": True,
            "isBestMatch": True,
        }
        trade = Trade(**data)
        assert trade.id == 123
        assert trade.price == Decimal("50000.00")
        assert trade.qty == Decimal("0.001")
        assert trade.is_buyer_maker is True


class TestAggregateTrade:
    """Tests for AggregateTrade model."""

    def test_aggregate_trade_parsing(self) -> None:
        """Test parsing aggregate trade data."""
        data = {
            "a": 12345,
            "p": "50000.00",
            "q": "1.0",
            "f": 100,
            "l": 105,
            "T": 1234567890000,
            "m": False,
        }
        agg_trade = AggregateTrade(**data)
        assert agg_trade.agg_trade_id == 12345
        assert agg_trade.price == Decimal("50000.00")
        assert agg_trade.quantity == Decimal("1.0")
        assert agg_trade.first_trade_id == 100
        assert agg_trade.last_trade_id == 105
        assert agg_trade.is_buyer_maker is False


class TestKline:
    """Tests for Kline model."""

    def test_from_list(self) -> None:
        """Test creating kline from list format."""
        data = [
            1234567890000,  # Open time
            "50000.00",  # Open
            "51000.00",  # High
            "49000.00",  # Low
            "50500.00",  # Close
            "100.0",  # Volume
            1234567899999,  # Close time
            "5050000.00",  # Quote volume
            500,  # Trade count
            "60.0",  # Taker buy base volume
            "3030000.00",  # Taker buy quote volume
            "0",  # Unused
        ]
        kline = Kline.from_list(data)
        assert kline.open_time == 1234567890000
        assert kline.open_price == Decimal("50000.00")
        assert kline.high_price == Decimal("51000.00")
        assert kline.low_price == Decimal("49000.00")
        assert kline.close_price == Decimal("50500.00")
        assert kline.volume == Decimal("100.0")
        assert kline.trade_count == 500


class TestTicker24hr:
    """Tests for Ticker24hr model."""

    def test_ticker_parsing(self) -> None:
        """Test parsing 24hr ticker data."""
        data = {
            "symbol": "BTCUSDT",
            "priceChange": "1000.00",
            "priceChangePercent": "2.00",
            "weightedAvgPrice": "50500.00",
            "prevClosePrice": "50000.00",
            "lastPrice": "51000.00",
            "lastQty": "0.1",
            "bidPrice": "50999.00",
            "bidQty": "1.0",
            "askPrice": "51001.00",
            "askQty": "2.0",
            "openPrice": "50000.00",
            "highPrice": "52000.00",
            "lowPrice": "49000.00",
            "volume": "1000.0",
            "quoteVolume": "50500000.00",
            "openTime": 1234567800000,
            "closeTime": 1234567899999,
            "firstId": 1,
            "lastId": 1000,
            "count": 1000,
        }
        ticker = Ticker24hr(**data)
        assert ticker.symbol == "BTCUSDT"
        assert ticker.price_change == Decimal("1000.00")
        assert ticker.last_price == Decimal("51000.00")
        assert ticker.count == 1000


class TestPriceTicker:
    """Tests for PriceTicker model."""

    def test_price_ticker_parsing(self) -> None:
        """Test parsing price ticker data."""
        data = {
            "symbol": "BTCUSDT",
            "price": "50000.00",
        }
        ticker = PriceTicker(**data)
        assert ticker.symbol == "BTCUSDT"
        assert ticker.price == Decimal("50000.00")


class TestBookTicker:
    """Tests for BookTicker model."""

    def test_book_ticker_parsing(self) -> None:
        """Test parsing book ticker data."""
        data = {
            "symbol": "BTCUSDT",
            "bidPrice": "50000.00",
            "bidQty": "1.0",
            "askPrice": "50001.00",
            "askQty": "2.0",
        }
        ticker = BookTicker(**data)
        assert ticker.symbol == "BTCUSDT"
        assert ticker.bid_price == Decimal("50000.00")
        assert ticker.ask_price == Decimal("50001.00")
