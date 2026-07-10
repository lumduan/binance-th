# StreamClient Reference

[Home](../index.md) > Reference > streams

**English** · [ไทย](../th/reference/streams.md)

**Module:** `binance_th.ws` · **Available since:** 1.0.0

WebSocket market streams (`client.ws`). Public — no credentials. Each `watch_*` is an **async
generator** you consume with `async for`; the connection reconnects automatically. Also builds a
self-syncing [`ManagedOrderBook`](#managedorderbook).

## Import

Accessed as `client.ws`.

## Methods

Every `watch_*` is an async generator that yields typed events until you `break` or the client closes.
Iterate with `async for` — do not `await` the call itself.

### watch_depth

```python
async def watch_depth(symbol: str) -> AsyncIterator[DepthUpdateEvent]
```
Incremental order-book diffs. For a maintained book, use [`order_book`](#order_book) instead.

### watch_trades

```python
async def watch_trades(symbol: str) -> AsyncIterator[TradeEvent]
```
Live trades.

```python
async with BinanceThClient() as client:
    async for t in client.ws.watch_trades("BTCTHB"):
        print(t.price, t.quantity)
        break
```

### watch_agg_trades

```python
async def watch_agg_trades(symbol: str) -> AsyncIterator[AggTradeEvent]
```
Live aggregate trades.

### watch_klines

```python
async def watch_klines(symbol: str, interval: str = "1m") -> AsyncIterator[KlineEvent]
```
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `interval` | `str` | `"1m"` | candle interval, e.g. `"1m"`, `"1h"` (a `KlineInterval` also works — it is a `str`) |

Live candles; each event's `.is_closed` marks the final tick of a candle.

### watch_book_ticker

```python
async def watch_book_ticker(symbol: str) -> AsyncIterator[BookTickerEvent]
```
Best bid/ask on every change.

### watch_ticker

```python
async def watch_ticker(symbol: str) -> AsyncIterator[TickerEvent]
```
Rolling 24-hour ticker updates.

### order_book

```python
async def order_book(symbol: str, *, limit: int = 1000) -> ManagedOrderBook
```
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `int` | `1000` | REST snapshot depth used to seed the book |

**Await it.** Returns a [`ManagedOrderBook`](#managedorderbook) — a local book kept in sync from a REST
snapshot plus the depth diff stream. Not yet started; call `start()`.

### aclose

```python
async def aclose() -> None
```
Closes all open streams and managed books. Called for you by `client.aclose()`.

---

## ManagedOrderBook

**Available since:** 1.0.0. A local order book that seeds from a REST snapshot and stays current from the
depth-diff stream. `Level` is `tuple[Decimal, Decimal]` — `(price, quantity)`.

### start

```python
async def start() -> None
```
Begins syncing (snapshot + diff replay) in the background. Call once.

### synced

```python
synced: bool  # property
```
`True` once the snapshot and the diff stream are reconciled.

### wait_synced

```python
async def wait_synced() -> None
```
Awaits until `synced` is `True`.

### best_bid / best_ask

```python
def best_bid() -> Level | None
def best_ask() -> Level | None
```
The top level per side, or `None` before sync.

### bids / asks

```python
def bids(n: int = 10) -> list[Level]
def asks(n: int = 10) -> list[Level]
```
The top `n` levels, best first.

### aclose

```python
async def aclose() -> None
```
Stops syncing and releases the stream.

```python
book = await client.ws.order_book("BTCTHB")
await book.start()
await book.wait_synced()
print(book.best_bid(), book.best_ask())
await book.aclose()
```

## See Also

- [Market streams guide](../guides/market-streams.md) · [Local order book guide](../guides/local-order-book.md)
- [WebSockets concept](../concepts/websockets.md) · [models](models.md)
