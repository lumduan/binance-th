"""Tests for user-data event models + the executionReport→Order mapper (M6).

Shapes are ⚠ASSUMED (standard Binance spot; not observed live — the M6 probe account was
idle). They pin the decode contract and the enum-coercion/fallback behaviour.
"""

from decimal import Decimal
from typing import Any

from binance_th.models.enums import OrderSide, OrderStatus, OrderType, TimeInForce
from binance_th.models.userdata import (
    BalanceUpdateEvent,
    ExecutionReportEvent,
    ListenKeyExpiredEvent,
    OutboundAccountPositionEvent,
    order_from_execution_report,
)

_EXEC_NEW: dict[str, Any] = {
    "e": "executionReport", "E": 1700000000000, "s": "BTCTHB", "c": "my-id", "S": "BUY",
    "o": "LIMIT", "f": "GTC", "q": "0.5", "p": "2100000", "P": "0", "x": "NEW", "X": "NEW",
    "r": "NONE", "i": 12345, "g": -1, "l": "0", "z": "0", "L": "0", "T": 1700000000001,
    "t": -1, "w": True, "m": False, "O": 1700000000000, "Z": "0", "Y": "0", "Q": "0",
}  # fmt: skip

_EXEC_FILL: dict[str, Any] = {
    "e": "executionReport", "E": 1700000009000, "s": "BTCTHB", "c": "my-id", "S": "SELL",
    "o": "LIMIT", "f": "GTC", "q": "0.5", "p": "2100000", "x": "TRADE", "X": "PARTIALLY_FILLED",
    "i": 12345, "l": "0.2", "z": "0.2", "L": "2100000", "n": "0.42", "N": "THB",
    "T": 1700000009001, "t": 999, "w": True, "m": True, "Z": "420000", "Y": "420000", "Q": "0",
}  # fmt: skip


class TestExecutionReportEvent:
    def test_parses_new(self) -> None:
        evt = ExecutionReportEvent.model_validate(_EXEC_NEW)
        assert evt.order_id == 12345
        assert evt.client_order_id == "my-id"
        assert evt.side == "BUY"  # raw str, not coerced
        assert evt.price == Decimal("2100000")
        assert evt.cumulative_filled_qty == Decimal("0")
        assert evt.current_order_status == "NEW"

    def test_raw_str_status_never_crashes(self) -> None:
        """An unmodeled status (e.g. PENDING_CANCEL) decodes as a raw string."""
        frame = {**_EXEC_NEW, "X": "PENDING_CANCEL"}
        evt = ExecutionReportEvent.model_validate(frame)
        assert evt.current_order_status == "PENDING_CANCEL"

    def test_extra_fields_preserved(self) -> None:
        evt = ExecutionReportEvent.model_validate({**_EXEC_NEW, "zz": "future"})
        assert evt.model_extra is not None and evt.model_extra.get("zz") == "future"


class TestOrderFromExecutionReport:
    def test_maps_new_order(self) -> None:
        order = order_from_execution_report(ExecutionReportEvent.model_validate(_EXEC_NEW))
        assert order.order_id == 12345
        assert order.status is OrderStatus.NEW
        assert order.side is OrderSide.BUY
        assert order.order_type is OrderType.LIMIT
        assert order.time_in_force is TimeInForce.GTC
        assert order.executed_qty == Decimal("0")
        assert order.is_working is True
        assert order.is_active is True

    def test_maps_partial_fill(self) -> None:
        order = order_from_execution_report(ExecutionReportEvent.model_validate(_EXEC_FILL))
        assert order.status is OrderStatus.PARTIALLY_FILLED
        assert order.side is OrderSide.SELL
        assert order.executed_qty == Decimal("0.2")
        assert order.cummulative_quote_qty == Decimal("420000")
        assert order.is_active is True

    def test_unknown_status_falls_back_to_new_and_stays_active(self) -> None:
        frame = {**_EXEC_NEW, "X": "PENDING_CANCEL", "w": None}
        order = order_from_execution_report(ExecutionReportEvent.model_validate(frame))
        assert order.status is OrderStatus.NEW  # safe fallback
        assert order.is_working is True  # unknown -> treated active, kept in the view

    def test_absent_optionals_fall_back(self) -> None:
        minimal = {
            "e": "executionReport", "E": 1700000000000, "s": "BTCTHB", "c": "c1", "S": "BUY",
            "o": "MARKET", "f": "GTC", "q": "1", "p": "0", "x": "NEW", "X": "NEW", "i": 7,
            "l": "0", "z": "0", "L": "0",
        }  # fmt: skip
        order = order_from_execution_report(ExecutionReportEvent.model_validate(minimal))
        assert order.time == 1700000000000  # O absent -> event_time
        assert order.update_time == 1700000000000  # T absent -> event_time
        assert order.cummulative_quote_qty == Decimal("0")  # Z absent -> 0
        assert order.orig_quote_order_qty == Decimal("0")  # Q absent -> 0


class TestBalanceEvents:
    def test_outbound_account_position(self) -> None:
        frame = {
            "e": "outboundAccountPosition", "E": 1700000000000, "u": 1700000000000,
            "B": [{"a": "THB", "f": "1000.5", "l": "0"}, {"a": "BTC", "f": "0.01", "l": "0.02"}],
        }  # fmt: skip
        evt = OutboundAccountPositionEvent.model_validate(frame)
        assert len(evt.balances) == 2
        assert evt.balances[0].asset == "THB"
        assert evt.balances[0].free == Decimal("1000.5")
        assert evt.balances[1].locked == Decimal("0.02")

    def test_balance_update_signed_delta(self) -> None:
        evt = BalanceUpdateEvent.model_validate(
            {"e": "balanceUpdate", "E": 1700000000000, "a": "THB", "d": "-1.5", "T": 1700000000001}
        )
        assert evt.asset == "THB"
        assert evt.balance_delta == Decimal("-1.5")

    def test_listen_key_expired(self) -> None:
        evt = ListenKeyExpiredEvent.model_validate({"e": "listenKeyExpired", "E": 1700000000000})
        assert evt.event_type == "listenKeyExpired"
        assert evt.listen_key is None
