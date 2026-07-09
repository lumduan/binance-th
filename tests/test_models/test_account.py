"""Tests for account/wallet model reconciliation (M3b defensive)."""

from binance_th.models.account import DepositAddress, DepositRecord, UserTrade, WithdrawRecord
from binance_th.models.enums import DepositStatus


class TestDefensiveReconciliation:
    """Fields that are plausibly null/absent on live TH now parse."""

    def test_user_trade_null_quote_qty(self) -> None:
        trade = UserTrade(
            symbol="BNBTHB",
            id=1,
            orderId=2,
            price="1",
            qty="1",
            quoteQty=None,
            commission="0",
            commissionAsset="BNB",
            time=1,
            isBuyer=True,
            isMaker=False,
            isBestMatch=True,
        )
        assert trade.quote_qty is None

    def test_deposit_address_optional_tag_url(self) -> None:
        addr = DepositAddress(address="x", coin="BTC")
        assert addr.tag is None
        assert addr.url is None

    def test_deposit_record_unknown_status_and_absent_ids(self) -> None:
        record = DepositRecord(
            amount="1",
            coin="BTC",
            network="BTC",
            status=4,
            address="a",
            insertTime=1,
            transferType=0,
            confirmTimes="1/1",
        )
        assert record.status == 4  # unknown-to-enum code, robust int, no crash
        assert record.tx_id is None
        assert record.address_tag is None
        # The int status still compares against the enum constants.
        ok = DepositRecord(
            amount="1",
            coin="BTC",
            network="BTC",
            status=1,
            address="a",
            insertTime=1,
            transferType=0,
            confirmTimes="1/1",
        )
        assert ok.status == DepositStatus.SUCCESS

    def test_withdraw_record_absent_txid(self) -> None:
        record = WithdrawRecord(
            address="a",
            amount="1",
            applyTime="2026",
            coin="BTC",
            id="w",
            network="BTC",
            transferType=0,
            status=6,
            transactionFee="0",
        )
        assert record.tx_id is None
        assert record.status == 6
