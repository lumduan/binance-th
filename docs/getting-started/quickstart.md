# Quickstart

[Home](../index.md) > Getting Started > Quickstart

**English** · [ไทย](../th/getting-started/quickstart.md)

This walks through a complete script — public data, a live order book, and a trade stream. No API key
required.

## The client is an async context manager

`BinanceThClient` owns its HTTP and WebSocket connections, so always open it with `async with`. On exit
it closes everything for you.

```python
import asyncio
from binance_th import BinanceThClient

async def main() -> None:
    async with BinanceThClient() as client:
        pong = await client.ping()
        print("reachable:", pong)

asyncio.run(main())
```

## Read market data (REST)

```python
async with BinanceThClient() as client:
    book = await client.market.depth("BTCTHB", limit=5)
    print("best bid:", book.bids[0].price, book.bids[0].quantity)

    last = await client.market.ticker_price("BTCTHB")
    print("last price:", last.price)   # a Decimal
```

Prices and quantities are `Decimal` — see [Money & Decimals](../concepts/money-and-decimals.md).

## Follow a live order book (WebSocket)

`client.ws.order_book(...)` returns a book that seeds from a REST snapshot and then keeps itself current
from the depth stream. You read it synchronously; it updates in the background.

```python
async with BinanceThClient() as client:
    order_book = await client.ws.order_book("BTCTHB")
    await order_book.wait_synced()          # first snapshot applied
    print("best bid:", order_book.best_bid())
    print("top 3 asks:", order_book.asks(3))
    await order_book.aclose()               # stop the background sync
```

## Stream trades (WebSocket)

`watch_*` methods are async iterators — loop over them with `async for`.

```python
async with BinanceThClient() as client:
    async for trade in client.ws.watch_trades("BTCTHB"):
        print(trade.price, trade.quantity, "maker" if trade.is_buyer_maker else "taker")
        break   # take one and stop
```

## Next steps

- Add credentials for account reads, orders, and the user-data stream:
  [Authentication](authentication.md).
- Understand the Thailand-specific symbol split: [GLOBAL vs SITE](../concepts/global-vs-site.md).
- Browse everything by task in the [guides](../guides/market-data.md).

## See Also

- [Market data guide](../guides/market-data.md)
- [Local order book guide](../guides/local-order-book.md)
- [API reference](../reference/index.md)
