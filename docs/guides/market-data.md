# Market data

[Home](../index.md) > Guides > Market data

**English** · [ไทย](../th/guides/market-data.md)

Everything under `client.market` is public — no credentials needed.

## Prerequisites

- [Installation](../getting-started/installation.md)
- [Money & Decimals](../concepts/money-and-decimals.md) — prices and quantities are `Decimal`

---

## Order book snapshot

```python
async with BinanceThClient() as client:
    book = await client.market.depth("BTCTHB", limit=20)
    print(book.last_update_id)
    print(book.bids[0].price, book.bids[0].quantity)   # best bid
    print(book.asks[0].price, book.asks[0].quantity)   # best ask
```

For a book that stays current, use the WebSocket [local order book](local-order-book.md) instead.

## Recent and aggregate trades

```python
trades = await client.market.trades("BTCTHB", limit=50)
aggs = await client.market.agg_trades("BTCTHB", limit=50)
for t in trades[:3]:
    print(t.price, t.qty, "maker" if t.is_buyer_maker else "taker")
```

## Klines (candles)

```python
from binance_th import KlineInterval

candles = await client.market.klines("BTCTHB", KlineInterval.HOUR_1, limit=100)
for k in candles[:3]:
    print(k.open_time, k.open_price, k.high_price, k.low_price, k.close_price, k.volume)
```

`interval` accepts the `KlineInterval` enum or a plain string like `"1h"`. For long date ranges that
exceed the per-call limit, use [pagination](pagination.md) (`iter_klines`).

## Tickers

```python
last = await client.market.ticker_price("BTCTHB")     # last price
stats = await client.market.ticker_24hr("BTCTHB")      # 24h rolling stats
top = await client.market.book_ticker("BTCTHB")        # best bid/ask
print(last.price, stats.price_change_percent, top.bid_price, top.ask_price)
```

## GLOBAL-only endpoints

`reference_price` and `execution_rules` exist only for GLOBAL symbols; a SITE/THB symbol returns a
`BinanceThBadRequestError`:

```python
ref = await client.market.reference_price("BTCUSDT")   # GLOBAL — ok
rules = await client.market.execution_rules()          # GLOBAL rules
```

See [GLOBAL vs SITE](../concepts/global-vs-site.md).

## See Also

- [Local order book guide](local-order-book.md) — a self-syncing book over WebSocket
- [Market streams guide](market-streams.md) — live trades/candles/tickers
- [Reference: market](../reference/market.md)
