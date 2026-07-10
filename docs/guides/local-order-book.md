# Local order book

[Home](../index.md) > Guides > Local order book

**English** · [ไทย](../th/guides/local-order-book.md)

`client.ws.order_book(symbol)` gives you an order book that stays in sync on its own: it seeds from a
REST snapshot, applies the live depth stream, and re-snapshots if it ever detects a gap. You read it
synchronously while it updates in the background.

## Prerequisites

- [Market streams](market-streams.md)
- [WebSockets](../concepts/websockets.md)

---

## Open a book

```python
async with BinanceThClient() as client:
    order_book = await client.ws.order_book("BTCTHB")
    await order_book.wait_synced()          # block until the first snapshot is applied
    try:
        print("best bid:", order_book.best_bid())   # (price, qty) or None
        print("best ask:", order_book.best_ask())
        print("top 5 bids:", order_book.bids(5))
        print("top 5 asks:", order_book.asks(5))
    finally:
        await order_book.aclose()
```

`order_book(...)` returns a `ManagedOrderBook` that's already started.

## Read methods

| Method | Returns |
|--------|---------|
| `book.best_bid()` / `book.best_ask()` | `(Decimal, Decimal)` or `None` |
| `book.bids(n=10)` / `book.asks(n=10)` | top-n `list[(Decimal, Decimal)]`, best first |
| `book.synced` | `bool` — has the first snapshot landed? |
| `await book.wait_synced()` | blocks until synced |
| `await book.aclose()` | stops the background sync (idempotent) |

Reads are cheap and never block; they return the current in-memory state.

## Poll it in a loop

```python
order_book = await client.ws.order_book("BTCTHB")
await order_book.wait_synced()
for _ in range(10):
    bid, ask = order_book.best_bid(), order_book.best_ask()
    print(bid, ask)
    await asyncio.sleep(1)
await order_book.aclose()
```

## How it stays correct

The engine follows the standard buffer→snapshot→apply algorithm: it buffers depth diffs, fetches the
REST snapshot, drops stale diffs, checks the first applied diff brackets the snapshot, and applies the
rest in order (a quantity of `0` removes a level). On any update-id gap — including after a reconnect —
it discards the book and re-snapshots, so you never read a silently-diverged book.

## See Also

- [Market streams guide](market-streams.md) — the raw `watch_depth` events
- [Reference: streams](../reference/streams.md) — `ManagedOrderBook`
