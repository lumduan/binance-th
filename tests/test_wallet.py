"""Tests for the signed WalletClient reads (M3b)."""

from decimal import Decimal

import httpx

from binance_th import BinanceThClient
from binance_th.config import BinanceThConfig
from binance_th.models.account import DepositAddress, DepositRecord, WithdrawRecord
from binance_th.timesync import TimeSync

from .conftest import Handler, TransportFactory


def _synced_ts(now: int = 1700000000000) -> TimeSync:
    ts = TimeSync(clock=lambda: now)
    ts.update(now)
    return ts


def _signed_client(mock_transport: TransportFactory, handler: Handler) -> BinanceThClient:
    transport, _ = mock_transport(
        handler, config=BinanceThConfig(api_key="K", api_secret="S"), timesync=_synced_ts()
    )
    return BinanceThClient(transport=transport)


def _deposit(tx_id: str, insert_time: int) -> dict[str, object]:
    return {
        "amount": "1",
        "coin": "BTC",
        "network": "BTC",
        "status": 1,
        "address": "a",
        "txId": tx_id,
        "insertTime": insert_time,
        "transferType": 0,
        "confirmTimes": "1/1",
    }


class TestWalletClient:
    """Signed wallet reads with defensive model handling."""

    async def test_deposit_address_no_tag_or_url(self, mock_transport: TransportFactory) -> None:
        """A deposit address without tag/url parses (defensive Optionals)."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"address": "abc", "coin": "BTC"})

        addr = await _signed_client(mock_transport, handler).wallet.deposit_address("BTC")
        assert isinstance(addr, DepositAddress)
        assert addr.address == "abc"
        assert addr.tag is None
        assert addr.url is None

    async def test_deposit_history_unknown_status_absent_ids(
        self, mock_transport: TransportFactory
    ) -> None:
        """A deposit with an unknown status code and absent txId/tag parses (no crash)."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json=[
                    {
                        "amount": "1.5",
                        "coin": "BTC",
                        "network": "BTC",
                        "status": 4,
                        "address": "abc",
                        "insertTime": 100,
                        "transferType": 0,
                        "confirmTimes": "1/1",
                    }
                ],
            )

        records = await _signed_client(mock_transport, handler).wallet.deposit_history(coin="BTC")
        assert isinstance(records[0], DepositRecord)
        assert records[0].status == 4
        assert records[0].amount == Decimal("1.5")
        assert records[0].tx_id is None
        assert records[0].address_tag is None

    async def test_withdraw_history_absent_txid(self, mock_transport: TransportFactory) -> None:
        """A processing withdrawal (no txId) parses."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json=[
                    {
                        "address": "abc",
                        "amount": "1",
                        "applyTime": "2026-01-01 00:00:00",
                        "coin": "BTC",
                        "id": "w1",
                        "network": "BTC",
                        "transferType": 0,
                        "status": 6,
                        "transactionFee": "0.0001",
                    }
                ],
            )

        records = await _signed_client(mock_transport, handler).wallet.withdraw_history()
        assert isinstance(records[0], WithdrawRecord)
        assert records[0].tx_id is None
        assert records[0].status == 6

    async def test_iter_deposit_history_paginates(self, mock_transport: TransportFactory) -> None:
        """iter_deposit_history walks windows and de-dups the boundary deposit by txId."""

        def handler(request: httpx.Request) -> httpx.Response:
            start = int(request.url.params.get("startTime", "0"))
            if start == 0:
                return httpx.Response(
                    200, json=[_deposit("x1", 0), _deposit("x2", 60000), _deposit("x3", 120000)]
                )
            if start == 120000:
                return httpx.Response(200, json=[_deposit("x3", 120000), _deposit("x4", 180000)])
            return httpx.Response(200, json=[])

        client = _signed_client(mock_transport, handler)
        tx_ids = [
            record.tx_id
            async for record in client.wallet.iter_deposit_history(
                start_time=0, end_time=200000, limit=3
            )
        ]
        assert tx_ids == ["x1", "x2", "x3", "x4"]
