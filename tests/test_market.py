"""Tests for the public MarketClient (M3a)."""

from decimal import Decimal

import httpx
import pytest

from binance_th import BinanceThClient
from binance_th.exceptions import BinanceThBadRequestError
from binance_th.market import _depth_weight
from binance_th.models.enums import KlineInterval
from binance_th.models.market import (
    AggregateTrade,
    BookTicker,
    ExecutionRules,
    Kline,
    OrderBook,
    PriceTicker,
    ReferencePrice,
    Ticker24hr,
    Trade,
)

from .conftest import Handler, TransportFactory


def _client(mock_transport: TransportFactory, handler: Handler) -> BinanceThClient:
    transport, _ = mock_transport(handler)
    return BinanceThClient(transport=transport)


def _kline(open_time: int) -> list[object]:
    return [open_time, "1", "2", "0.5", "1.5", "100", open_time + 59999, "150", 5, "40", "60", "0"]


class TestMarketClient:
    """Each endpoint returns the right typed model from a bare body."""

    async def test_depth(self, mock_transport: TransportFactory) -> None:
        """depth parses lastUpdateId/bids/asks into Decimals."""

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/api/v1/depth"
            assert request.url.params["symbol"] == "BTCUSDT"
            return httpx.Response(
                200,
                json={"lastUpdateId": 42, "bids": [["100.5", "1.0"]], "asks": [["101.0", "2.0"]]},
            )

        book = await _client(mock_transport, handler).market.depth("BTCUSDT", limit=5)
        assert isinstance(book, OrderBook)
        assert book.last_update_id == 42
        assert book.bids[0].price == Decimal("100.5")
        assert book.asks[0].quantity == Decimal("2.0")

    async def test_trades_null_quote_qty(self, mock_transport: TransportFactory) -> None:
        """A SITE symbol's null quoteQty parses to None."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json=[
                    {
                        "id": 1,
                        "price": "10",
                        "qty": "2",
                        "quoteQty": None,
                        "time": 1,
                        "isBuyerMaker": True,
                        "isBestMatch": False,
                    }
                ],
            )

        trades = await _client(mock_transport, handler).market.trades("BNBTHB")
        assert isinstance(trades[0], Trade)
        assert trades[0].quote_qty is None

    async def test_agg_trades(self, mock_transport: TransportFactory) -> None:
        """aggTrades parses single-letter aliases."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200, json=[{"a": 1, "p": "10", "q": "2", "f": 1, "l": 3, "T": 9, "m": True}]
            )

        aggs = await _client(mock_transport, handler).market.agg_trades("BTCUSDT")
        assert isinstance(aggs[0], AggregateTrade)
        assert aggs[0].agg_trade_id == 1

    async def test_klines(self, mock_transport: TransportFactory) -> None:
        """klines parses the 12-field arrays; interval serializes to '1m'."""

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.params["interval"] == "1m"
            return httpx.Response(200, json=[_kline(1700000000000)])

        ks = await _client(mock_transport, handler).market.klines(
            "BTCUSDT", KlineInterval.MINUTE_1, limit=1
        )
        assert isinstance(ks[0], Kline)
        assert ks[0].open_time == 1700000000000
        assert ks[0].close_price == Decimal("1.5")

    async def test_ticker_24hr_site_nulls(self, mock_transport: TransportFactory) -> None:
        """A SITE ticker with null qty fields parses to None."""
        body = {
            "symbol": "BNBTHB",
            "priceChange": "1",
            "priceChangePercent": "0.5",
            "weightedAvgPrice": "10",
            "prevClosePrice": None,
            "lastPrice": "11",
            "lastQty": None,
            "bidPrice": "10",
            "bidQty": None,
            "askPrice": "12",
            "askQty": None,
            "openPrice": "10",
            "highPrice": "12",
            "lowPrice": "9",
            "volume": "100",
            "quoteVolume": "1000",
            "openTime": 1,
            "closeTime": 2,
            "firstId": 1,
            "lastId": 2,
            "count": 2,
        }

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json=body)

        ticker = await _client(mock_transport, handler).market.ticker_24hr("BNBTHB")
        assert isinstance(ticker, Ticker24hr)
        assert ticker.prev_close_price is None
        assert ticker.last_qty is None
        assert ticker.bid_qty is None
        assert ticker.ask_qty is None
        assert ticker.last_price == Decimal("11")

    async def test_ticker_price_and_book(self, mock_transport: TransportFactory) -> None:
        """ticker_price and book_ticker parse their objects."""

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path.endswith("/price"):
                return httpx.Response(200, json={"symbol": "BTCUSDT", "price": "62000"})
            return httpx.Response(
                200,
                json={
                    "symbol": "BTCUSDT",
                    "bidPrice": "61999",
                    "bidQty": "1",
                    "askPrice": "62001",
                    "askQty": "2",
                },
            )

        client = _client(mock_transport, handler)
        price = await client.market.ticker_price("BTCUSDT")
        assert isinstance(price, PriceTicker)
        assert price.price == Decimal("62000")
        book = await client.market.book_ticker("BTCUSDT")
        assert isinstance(book, BookTicker)
        assert book.ask_price == Decimal("62001")

    async def test_reference_price(self, mock_transport: TransportFactory) -> None:
        """reference_price parses for a GLOBAL symbol."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200, json={"symbol": "BTCUSDT", "referencePrice": "62000", "timestamp": 9}
            )

        rp = await _client(mock_transport, handler).market.reference_price("BTCUSDT")
        assert isinstance(rp, ReferencePrice)
        assert rp.reference_price == Decimal("62000")

    async def test_reference_price_site_400(self, mock_transport: TransportFactory) -> None:
        """A SITE symbol 400 {code:-1000} surfaces as BinanceThBadRequestError."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(400, json={"code": -1000, "msg": "unsupported symbol"})

        with pytest.raises(BinanceThBadRequestError):
            await _client(mock_transport, handler).market.reference_price("BNBTHB")

    async def test_execution_rules(self, mock_transport: TransportFactory) -> None:
        """executionRules parses the nested PRICE_RANGE (null multipliers)."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "symbolRules": [
                        {
                            "symbol": "BTCUSDT",
                            "rules": [
                                {
                                    "ruleType": "PRICE_RANGE",
                                    "bidMultiplierUp": None,
                                    "bidMultiplierDown": None,
                                    "askMultiplierUp": None,
                                    "askMultiplierDown": None,
                                }
                            ],
                        }
                    ]
                },
            )

        rules = await _client(mock_transport, handler).market.execution_rules()
        assert isinstance(rules, ExecutionRules)
        entry = rules.get_symbol("BTCUSDT")
        assert entry is not None
        assert entry.rules[0].rule_type == "PRICE_RANGE"
        assert entry.rules[0].bid_multiplier_up is None

    async def test_execution_rules_site_400(self, mock_transport: TransportFactory) -> None:
        """A SITE executionRules 400 surfaces as BinanceThBadRequestError."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(400, json={"code": -1000, "msg": "unsupported"})

        with pytest.raises(BinanceThBadRequestError):
            await _client(mock_transport, handler).market.execution_rules()

    async def test_iter_klines_paginates_and_dedups(self, mock_transport: TransportFactory) -> None:
        """iter_klines walks windows and de-dups the inclusive-startTime boundary candle."""

        def handler(request: httpx.Request) -> httpx.Response:
            start = int(request.url.params.get("startTime", "0"))
            if start == 0:
                return httpx.Response(200, json=[_kline(0), _kline(60000), _kline(120000)])
            if start == 120000:
                return httpx.Response(200, json=[_kline(120000), _kline(180000)])
            return httpx.Response(200, json=[])

        client = _client(mock_transport, handler)
        opens = [
            k.open_time
            async for k in client.market.iter_klines(
                "BTCUSDT", KlineInterval.MINUTE_1, start_time=0, end_time=200000, limit=3
            )
        ]
        assert opens == [0, 60000, 120000, 180000]


class TestDepthWeight:
    """The depth weight bands (ASSUMED)."""

    @pytest.mark.parametrize(
        ("limit", "weight"), [(None, 1), (100, 1), (500, 5), (1000, 10), (5000, 50)]
    )
    def test_bands(self, limit: int | None, weight: int) -> None:
        assert _depth_weight(limit) == weight
