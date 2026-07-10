# Models Reference

[Home](../index.md) > Reference > models

**Module:** `binance_th.models` · **Available since:** 1.0.0

Every public Pydantic model and enum. You rarely construct these yourself — the client returns them — but
knowing their fields and value sets is what makes the typed API useful.

## Import

```python
from binance_th.models import Order, OrderBook, Ticker24hr, KlineInterval  # …etc
```

All model and enum names are also re-exported from the package root (`from binance_th import Order`).

## Conventions

- **Two base classes.** Responses subclass `ResponseModel` (`extra="allow"` — unknown API fields are
  kept, not dropped). Requests subclass `RequestModel` (`extra="forbid"` — typos are rejected before
  sending). Both accept snake_case **or** the camelCase alias and strip whitespace.
- **`Decimal` for money.** Every price, quantity, balance, fee, and commission is a `Decimal`, never a
  `float`.
- **snake_case ↔ camelCase.** Your code uses `order_id`; the wire uses `orderId`. The alias is set per
  field.
- **Array-format endpoints need classmethods.** A few responses are positional arrays, not JSON objects,
  so they are built with a classmethod, not `Model(**data)`:

  | Model | Classmethod |
  |-------|-------------|
  | `OrderBookEntry` | `OrderBookEntry.from_list([price, qty])` |
  | `OrderBook` | `OrderBook.from_api(raw_dict)` |
  | `Kline` | `Kline.from_list([...])` |

## Response models

| Group | Models |
|-------|--------|
| Base / meta | `ServerTime`, `ExchangeInfo`, `SymbolInfo`, `SymbolFilter`, `SymbolTypeInfo`, `RateLimit` |
| Market | `OrderBook`, `OrderBookEntry`, `Trade`, `AggregateTrade`, `Kline`, `Ticker24hr`, `PriceTicker`, `BookTicker`, `ReferencePrice`, `ExecutionRules`, `SymbolExecutionRules`, `ExecutionRule` |
| Account / wallet ⚠ | `AccountInfo`, `Balance`, `TradeFee`, `UserTrade`, `DepositAddress`, `DepositRecord`, `WithdrawRecord`, `WithdrawResult`, `SubAccountTransfer`, `ListenKey` |
| Orders | `Order` |
| Market-stream events | `StreamMessage`, `DepthUpdateEvent`, `TradeEvent`, `AggTradeEvent`, `KlineEvent`, `KlineData`, `BookTickerEvent`, `TickerEvent` |
| User-data events ⚠ | `ExecutionReportEvent`, `OutboundAccountPositionEvent`, `AccountBalanceDelta`, `BalanceUpdateEvent`, `ListenKeyExpiredEvent` |

> ⚠ The account/wallet and user-data models follow the documented Binance-TH schema but are not all
> confirmed against live responses. `extra="allow"` preserves anything unmodelled. See
> [Assumed shapes](../concepts/assumed-shapes.md). Market-stream event shapes were verified live
> (2026-07-09), with some GLOBAL-vs-SITE fields optional (no-parity, ADR-0011).

## Request models

Subclass `RequestModel` (`extra="forbid"`). They deliberately omit `timestamp`/`signature` — the client
adds those when signing.

| Model | Purpose | Validation |
|-------|---------|-----------|
| `OrderRequest` | build a `create_order` payload | LIMIT ⇒ price + timeInForce + quantity; MARKET ⇒ quantity **or** quoteOrderQty; STOP\* ⇒ stopPrice |
| `CancelOrderRequest` | cancel by id | requires `order_id` **or** `orig_client_order_id` |
| `QueryOrderRequest` | query by id | requires `order_id` **or** `orig_client_order_id` |

## Enums

All are `StrEnum` (compare/serialize as their string value) except `DepositStatus`/`WithdrawStatus`,
which are `int` enums.

| Enum | Members (value) |
|------|-----------------|
| `OrderSide` | `BUY`, `SELL` |
| `OrderType` | `LIMIT`, `MARKET`, `STOP_LOSS`, `STOP_LOSS_LIMIT`, `TAKE_PROFIT`, `TAKE_PROFIT_LIMIT`, `LIMIT_MAKER` |
| `OrderStatus` | `NEW`, `PARTIALLY_FILLED`, `FILLED`, `CANCELED`, `REJECTED`, `EXPIRED` |
| `TimeInForce` | `GTC`, `IOC`, `FOK` |
| `KlineInterval` | `MINUTE_1`…`MINUTE_30` (`1m,3m,5m,15m,30m`), `HOUR_1`…`HOUR_12` (`1h,2h,4h,6h,8h,12h`), `DAY_1`/`DAY_3` (`1d,3d`), `WEEK_1` (`1w`), `MONTH_1` (`1M`) |
| `SymbolType` | `GLOBAL`, `SITE` |
| `SymbolStatus` | `TRADING`, `HALT`, `BREAK` |
| `RateLimitType` | `REQUEST_WEIGHT`, `ORDERS`, `RAW_REQUESTS` |
| `RateLimitInterval` | `SECOND`, `MINUTE`, `HOUR`, `DAY` |
| `FilterType` | `PRICE_FILTER`, `PERCENT_PRICE`, `LOT_SIZE`, `MIN_NOTIONAL`, `ICEBERG_PARTS`, `MARKET_LOT_SIZE`, `MAX_NUM_ORDERS`, `MAX_NUM_ALGO_ORDERS`, `MAX_NUM_ICEBERG_ORDERS`, `EXCHANGE_MAX_NUM_ORDERS`, `EXCHANGE_MAX_NUM_ALGO_ORDERS` |
| `DepositStatus` (int) | `PENDING=0`, `SUCCESS=1`, `CREDITED=6` |
| `WithdrawStatus` (int) | `EMAIL_SENT=0`, `CANCELLED=1`, `AWAITING_APPROVAL=2`, `REJECTED=3`, `PROCESSING=4`, `FAILURE=5`, `COMPLETED=6` |

## Convenience members

| On | Member | Gives |
|----|--------|-------|
| `ExchangeInfo` | `get_symbol(sym)` | `SymbolInfo \| None` |
| `ExecutionRules` | `get_symbol(sym)` | `SymbolExecutionRules \| None` |
| `AccountInfo` | `get_balance(asset)`, `get_non_zero_balances()` | `Balance \| None`, `list[Balance]` |
| `Balance` | `total` | `free + locked` |
| `Order` | `is_filled`, `is_active`, `filled_percent` | order-state helpers |
| `binance_th.models` | `order_from_execution_report(evt)` | an `Order` built from an `ExecutionReportEvent` |

## See Also

- [Money & Decimals](../concepts/money-and-decimals.md) · [Assumed shapes](../concepts/assumed-shapes.md)
- [market](market.md) · [orders](orders.md) · [streams](streams.md)
