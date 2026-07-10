# Market streams

[Home](../index.md) > Guides > Market streams

`client.ws` gives you live market data over WebSocket as async iterators. All of it is public — no
credentials needed.

## Prerequisites

- [Quickstart](../getting-started/quickstart.md)
- [WebSockets](../concepts/websockets.md) — reconnection and routing

---

## The `watch_*` iterators

Each returns an async iterator of typed events — loop with `async for`:

| Method | Yields |
|--------|--------|
| `client.ws.watch_depth(symbol)` | `DepthUpdateEvent` (raw diff-depth) |
| `client.ws.watch_trades(symbol)` | `TradeEvent` |
| `client.ws.watch_agg_trades(symbol)` | `AggTradeEvent` |
| `client.ws.watch_klines(symbol, interval="1m")` | `KlineEvent` |
| `client.ws.watch_book_ticker(symbol)` | `BookTickerEvent` |
| `client.ws.watch_ticker(symbol)` | `TickerEvent` |

```python
async with BinanceThClient() as client:
    async for trade in client.ws.watch_trades("BTCTHB"):
        print(trade.price, trade.quantity)
```

## Candles

```python
async for k in client.ws.watch_klines("BTCTHB", "1m"):
    if k.kline.is_closed:                 # act only on finalized candles
        print(k.kline.close_price, k.kline.volume)
```

## Watching several streams at once

Kick off each iterator as a task:

```python
import asyncio

async def pump(agen, label):
    async for evt in agen:
        print(label, evt)

async with BinanceThClient() as client:
    await asyncio.gather(
        pump(client.ws.watch_trades("BTCTHB"), "trade"),
        pump(client.ws.watch_book_ticker("BTCTHB"), "book"),
    )
```

The client multiplexes them onto as few connections as possible (one per host).

## Stopping

Breaking out of the loop unsubscribes that stream; leaving the `async with` (or `await client.ws.aclose()`)
tears the connections down cleanly. Reconnection while streaming is automatic — see
[WebSockets](../concepts/websockets.md).

## Depth vs a synced book

`watch_depth` gives you the raw diff-depth events. If what you actually want is a maintained order book,
use [`order_book`](local-order-book.md) — it applies those diffs to a REST snapshot for you.

## See Also

- [Local order book guide](local-order-book.md)
- [Reference: streams](../reference/streams.md)
