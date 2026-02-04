"""Pydantic models for Binance Thailand API.

This module exports all model classes used for API requests and responses.

Model Categories:
- Enums: Order types, sides, statuses, intervals
- Base: Common response/request models, exchange info
- Market: Order book, trades, klines, tickers
- Account: Balances, deposits, withdrawals, user data
- Orders: Order creation, querying, cancellation

Example:
    >>> from binance_th.models import OrderSide, OrderType, Order
    >>> from binance_th.models import Ticker24hr, OrderBook
"""

from binance_th.models.account import (
    AccountInfo,
    Balance,
    DepositAddress,
    DepositRecord,
    ListenKey,
    SubAccountTransfer,
    TradeFee,
    UserTrade,
    WithdrawRecord,
    WithdrawResult,
)
from binance_th.models.base import (
    ExchangeInfo,
    RateLimit,
    RequestModel,
    ResponseModel,
    ServerTime,
    SymbolFilter,
    SymbolInfo,
    SymbolTypeInfo,
)
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
from binance_th.models.orders import (
    CancelOrderRequest,
    Order,
    OrderRequest,
    QueryOrderRequest,
)

__all__ = [
    "AccountInfo",
    "AggregateTrade",
    # Account models
    "Balance",
    "BookTicker",
    "CancelOrderRequest",
    "DepositAddress",
    "DepositRecord",
    "DepositStatus",
    "ExchangeInfo",
    "FilterType",
    "Kline",
    "KlineInterval",
    "ListenKey",
    # Order models
    "Order",
    "OrderBook",
    # Market models
    "OrderBookEntry",
    "OrderRequest",
    # Enums
    "OrderSide",
    "OrderStatus",
    "OrderType",
    "PriceTicker",
    "QueryOrderRequest",
    "RateLimit",
    "RateLimitInterval",
    "RateLimitType",
    "RequestModel",
    # Base models
    "ResponseModel",
    "ServerTime",
    "SubAccountTransfer",
    "SymbolFilter",
    "SymbolInfo",
    "SymbolStatus",
    "SymbolType",
    "SymbolTypeInfo",
    "Ticker24hr",
    "TimeInForce",
    "Trade",
    "TradeFee",
    "UserTrade",
    "WithdrawRecord",
    "WithdrawResult",
    "WithdrawStatus",
]
