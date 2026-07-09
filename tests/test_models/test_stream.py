"""Tests for WebSocket stream event models (M5).

Payloads are the real frames captured live on 2026-07-09 by ``scripts/probe_ws.py``
(GLOBAL = BTCUSDT on /gstream, SITE = BTCTHB on /nstream). They assert the verified
GLOBAL/SITE shape differences (ADR-0011 no-parity) round-trip correctly.
"""

from decimal import Decimal

from binance_th.models.market import OrderBookEntry
from binance_th.models.stream import (
    AggTradeEvent,
    BookTickerEvent,
    DepthUpdateEvent,
    KlineEvent,
    StreamMessage,
    TickerEvent,
    TradeEvent,
)

# --- Real captured frames -------------------------------------------------------------

GLOBAL_DEPTH = {
    "e": "depthUpdate",
    "E": 1783605717014,
    "s": "BTCUSDT",
    "U": 97201195665,
    "u": 97201195871,
    "b": [["63035.96000000", "3.18600000"], ["63032.50000000", "0.00009000"]],
    "a": [["63035.97000000", "0.00000000"]],
}
SITE_DEPTH = {
    "e": "depthUpdate",
    "E": 1783605724750,
    "T": 1783605724720,
    "s": "BTCTHB",
    "U": 3103354139,
    "u": 3103354168,
    "pu": 3103354134,
    "b": [["2099839.00", "0.45672000"]],
    "a": [["2102041.00", "0.00000000"], ["2102571.00", "0.07613000"]],
}
GLOBAL_TRADE = {
    "e": "trade", "E": 1783605833143, "s": "BTCUSDT", "t": 6492563658,
    "p": "63082.66000000", "q": "0.00126000", "T": 1783605833143, "m": True, "M": True,
}  # fmt: skip
SITE_TRADE = {
    "e": "trade", "E": 1783605843347, "T": 1783605843336, "s": "BTCTHB",
    "t": 2536552, "p": "2102876.00", "q": "0.00854000", "m": True,
}  # fmt: skip
GLOBAL_AGG = {
    "e": "aggTrade", "E": 1783605833143, "s": "BTCUSDT", "a": 4010355719,
    "p": "63082.66000000", "q": "0.00126000", "f": 6492563658, "l": 6492563658,
    "T": 1783605833143, "m": True, "M": True,
}  # fmt: skip
SITE_AGG = {
    "e": "aggTrade", "E": 1783605843498, "a": 2395912, "s": "BTCTHB",
    "p": "2102876.00", "q": "0.00855000", "f": 2536552, "l": 2536553,
    "T": 1783605843336, "m": True,
}  # fmt: skip
KLINE = {
    "e": "kline", "E": 1783605834037, "s": "BTCUSDT",
    "k": {
        "t": 1783605780000, "T": 1783605839999, "s": "BTCUSDT", "i": "1m",
        "f": 6492559321, "L": 6492563661, "o": "63031.52000000", "c": "63082.66000000",
        "h": "63082.67000000", "l": "62978.00000000", "v": "6.78294000", "n": 4341,
        "x": False, "q": "427455.65631630", "V": "3.12788000", "Q": "197160.86587150", "B": "0",
    },
}  # fmt: skip
GLOBAL_BOOK = {
    "u": 97201195816, "s": "BTCUSDT", "b": "63035.96000000",
    "B": "3.18600000", "a": "63035.97000000", "A": "1.04466000",
}  # fmt: skip
SITE_BOOK = {
    "u": 3103354229, "e": "bookTicker", "s": "BTCTHB", "b": "2102044.00",
    "B": "0.01872000", "a": "2102597.00", "A": "0.00072000",
    "T": 1783605725183, "E": 1783605725194,
}  # fmt: skip
GLOBAL_TICKER = {
    "e": "24hrTicker", "E": 1783605717016, "s": "BTCUSDT", "p": "1028.96000000",
    "P": "1.659", "w": "62403.11713050", "x": "62007.00000000", "c": "63035.96000000",
    "Q": "0.03108000", "b": "63035.96000000", "B": "3.18600000", "a": "63035.97000000",
    "A": "1.04465000", "o": "62007.00000000", "h": "63283.26000000", "l": "61544.56000000",
    "v": "17804.24715000", "q": "1111040520.32181630", "O": 1783519317000, "C": 1783605717000,
    "F": 1000, "L": 2000, "n": 1001,
}  # fmt: skip


class TestStreamMessage:
    def test_combined_envelope(self) -> None:
        msg = StreamMessage.model_validate({"stream": "btcthb@depth", "data": SITE_DEPTH})
        assert msg.stream == "btcthb@depth"
        assert msg.data["s"] == "BTCTHB"


class TestDepthUpdateEvent:
    def test_global_has_no_pu_or_t(self) -> None:
        d = DepthUpdateEvent.model_validate(GLOBAL_DEPTH)
        assert d.symbol == "BTCUSDT"
        assert d.first_update_id == 97201195665
        assert d.final_update_id == 97201195871
        assert d.prev_final_update_id is None
        assert d.transaction_time is None

    def test_site_carries_pu_and_t(self) -> None:
        d = DepthUpdateEvent.model_validate(SITE_DEPTH)
        assert d.prev_final_update_id == 3103354134
        assert d.transaction_time == 1783605724720

    def test_levels_parse_to_decimal_entries(self) -> None:
        d = DepthUpdateEvent.model_validate(GLOBAL_DEPTH)
        assert isinstance(d.bids[0], OrderBookEntry)
        assert d.bids[0].price == Decimal("63035.96000000")
        assert d.bids[0].quantity == Decimal("3.18600000")
        # quantity 0 is preserved (the sync engine treats it as a removal)
        assert d.asks[0].quantity == Decimal("0")


class TestTradeEvent:
    def test_global_has_best_match(self) -> None:
        t = TradeEvent.model_validate(GLOBAL_TRADE)
        assert t.trade_id == 6492563658
        assert t.price == Decimal("63082.66000000")
        assert t.is_best_match is True
        assert t.transaction_time == 1783605833143

    def test_site_omits_best_match(self) -> None:
        t = TradeEvent.model_validate(SITE_TRADE)
        assert t.is_best_match is None
        assert t.is_buyer_maker is True
        assert t.transaction_time == 1783605843336


class TestAggTradeEvent:
    def test_global(self) -> None:
        a = AggTradeEvent.model_validate(GLOBAL_AGG)
        assert a.agg_trade_id == 4010355719
        assert a.first_trade_id == 6492563658
        assert a.last_trade_id == 6492563658
        assert a.is_best_match is True

    def test_site_omits_best_match(self) -> None:
        a = AggTradeEvent.model_validate(SITE_AGG)
        assert a.is_best_match is None
        assert a.quantity == Decimal("0.00855000")


class TestKlineEvent:
    def test_nested_kline_data(self) -> None:
        k = KlineEvent.model_validate(KLINE)
        assert k.symbol == "BTCUSDT"
        assert k.kline.interval == "1m"
        assert k.kline.is_closed is False
        assert k.kline.open_price == Decimal("63031.52000000")
        assert k.kline.close_price == Decimal("63082.66000000")
        assert k.kline.trade_count == 4341
        assert k.kline.quote_volume == Decimal("427455.65631630")


class TestBookTickerEvent:
    def test_global_omits_event_envelope(self) -> None:
        b = BookTickerEvent.model_validate(GLOBAL_BOOK)
        assert b.update_id == 97201195816
        assert b.bid_price == Decimal("63035.96000000")
        assert b.ask_qty == Decimal("1.04466000")
        assert b.event_type is None
        assert b.event_time is None
        assert b.transaction_time is None

    def test_site_carries_event_envelope(self) -> None:
        b = BookTickerEvent.model_validate(SITE_BOOK)
        assert b.event_type == "bookTicker"
        assert b.event_time == 1783605725194
        assert b.transaction_time == 1783605725183


class TestTickerEvent:
    def test_global_full_stats(self) -> None:
        t = TickerEvent.model_validate(GLOBAL_TICKER)
        assert t.symbol == "BTCUSDT"
        assert t.last_price == Decimal("63035.96000000")
        assert t.price_change_percent == Decimal("1.659")
        assert t.trade_count == 1001
        assert t.high_price == Decimal("63283.26000000")


class TestByFieldName:
    def test_populate_by_name(self) -> None:
        """populate_by_name allows constructing by the snake_case attribute name."""
        d = DepthUpdateEvent(
            event_type="depthUpdate",
            event_time=1,
            symbol="BTCTHB",
            first_update_id=10,
            final_update_id=20,
            bids=[OrderBookEntry(price=Decimal("1"), quantity=Decimal("2"))],
            asks=[],
        )
        assert d.symbol == "BTCTHB"
        assert d.bids[0].price == Decimal("1")
