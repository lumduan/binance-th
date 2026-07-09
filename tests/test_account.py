"""Tests for the signed AccountClient (M3b)."""

import hashlib
import hmac
from decimal import Decimal

import httpx
import pytest

from binance_th import BinanceThClient
from binance_th.config import BinanceThConfig
from binance_th.exceptions import BinanceThAuthError
from binance_th.models.account import AccountInfo, TradeFee, UserTrade
from binance_th.timesync import TimeSync

from .conftest import Handler, TransportFactory


def _synced_ts(now: int = 1700000000000) -> TimeSync:
    ts = TimeSync(clock=lambda: now)
    ts.update(now)
    return ts


def _signed_client(
    mock_transport: TransportFactory, handler: Handler
) -> tuple[BinanceThClient, list[httpx.Request]]:
    transport, captured = mock_transport(
        handler, config=BinanceThConfig(api_key="KEY", api_secret="SECRET"), timesync=_synced_ts()
    )
    return BinanceThClient(transport=transport), captured


def _trade(trade_id: int, time_ms: int) -> dict[str, object]:
    return {
        "symbol": "BTCTHB",
        "id": trade_id,
        "orderId": trade_id,
        "price": "1",
        "qty": "1",
        "quoteQty": "1",
        "commission": "0",
        "commissionAsset": "BTC",
        "time": time_ms,
        "isBuyer": True,
        "isMaker": False,
        "isBestMatch": True,
    }


class TestAccountClient:
    """Signed account reads."""

    async def test_account_signed(self, mock_transport: TransportFactory) -> None:
        """account() returns AccountInfo and carries the api-key header + trailing signature."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "makerCommission": 10,
                    "takerCommission": 10,
                    "buyerCommission": 0,
                    "sellerCommission": 0,
                    "canTrade": True,
                    "canWithdraw": True,
                    "canDeposit": True,
                    "updateTime": 1,
                    "balances": [{"asset": "THB", "free": "100.5", "locked": "0"}],
                },
            )

        client, captured = _signed_client(mock_transport, handler)
        info = await client.account.account()
        assert isinstance(info, AccountInfo)
        balance = info.get_balance("THB")
        assert balance is not None
        assert balance.free == Decimal("100.5")

        request = captured[-1]
        assert request.headers["X-MBX-APIKEY"] == "KEY"
        query = request.url.query.decode()
        assert query.split("&")[-1].startswith("signature=")
        expected = hmac.new(
            b"SECRET", b"recvWindow=5000&timestamp=1700000000000", hashlib.sha256
        ).hexdigest()
        assert f"signature={expected}" in query

    async def test_trade_fees_list(self, mock_transport: TransportFactory) -> None:
        """trade_fees parses a list response."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json=[{"symbol": "BTCTHB", "makerCommission": "0.001", "takerCommission": "0.001"}],
            )

        client, _ = _signed_client(mock_transport, handler)
        fees = await client.account.trade_fees(symbol="BTCTHB")
        assert isinstance(fees[0], TradeFee)
        assert fees[0].maker_commission == Decimal("0.001")

    async def test_trade_fees_single_object_defensive(
        self, mock_transport: TransportFactory
    ) -> None:
        """trade_fees tolerates a single-object response (list-vs-single is unverified)."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={"symbol": "BTCTHB", "makerCommission": "0.001", "takerCommission": "0.001"},
            )

        client, _ = _signed_client(mock_transport, handler)
        fees = await client.account.trade_fees()
        assert len(fees) == 1
        assert fees[0].symbol == "BTCTHB"

    async def test_user_trades_null_quote_qty(self, mock_transport: TransportFactory) -> None:
        """A SITE user trade with null quoteQty parses (defensive reconciliation)."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json=[
                    {
                        "symbol": "BNBTHB",
                        "id": 1,
                        "orderId": 2,
                        "price": "10",
                        "qty": "1",
                        "quoteQty": None,
                        "commission": "0.01",
                        "commissionAsset": "BNB",
                        "time": 100,
                        "isBuyer": True,
                        "isMaker": False,
                        "isBestMatch": True,
                    }
                ],
            )

        client, _ = _signed_client(mock_transport, handler)
        trades = await client.account.user_trades("BNBTHB")
        assert isinstance(trades[0], UserTrade)
        assert trades[0].quote_qty is None

    async def test_iter_user_trades_paginates(self, mock_transport: TransportFactory) -> None:
        """iter_user_trades walks windows and de-dups the boundary trade by id."""

        def handler(request: httpx.Request) -> httpx.Response:
            start = int(request.url.params.get("startTime", "0"))
            if start == 0:
                return httpx.Response(200, json=[_trade(1, 0), _trade(2, 60000), _trade(3, 120000)])
            if start == 120000:
                return httpx.Response(200, json=[_trade(3, 120000), _trade(4, 180000)])
            return httpx.Response(200, json=[])

        client, _ = _signed_client(mock_transport, handler)
        ids = [
            trade.id
            async for trade in client.account.iter_user_trades(
                "BTCTHB", start_time=0, end_time=200000, limit=3
            )
        ]
        assert ids == [1, 2, 3, 4]

    async def test_signed_without_credentials_raises(
        self, mock_transport: TransportFactory
    ) -> None:
        """A signed read without credentials raises before any network hit."""

        def handler(_request: httpx.Request) -> httpx.Response:  # pragma: no cover - never called
            return httpx.Response(200, json={})

        transport, captured = mock_transport(handler, config=BinanceThConfig())
        client = BinanceThClient(transport=transport)
        with pytest.raises(BinanceThAuthError):
            await client.account.account()
        assert captured == []
