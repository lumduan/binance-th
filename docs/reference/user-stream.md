# UserDataStream Reference

[Home](../index.md) > Reference > user-stream

**English** · [ไทย](../th/reference/user-stream.md)

**Module:** `binance_th.user_stream` · **Available since:** 1.0.0

The user-data stream (`client.user_stream`) — live order, account, and balance updates for your account.
Authenticated with your **API key** (a listenKey is created and kept alive for you); it does not use
request signing. Binance-TH issues **separate listenKeys per symbol type** (GLOBAL vs SITE), which this
client manages transparently.

> ⚠ **Assumed shapes.** User-data event models follow the documented schema but are not all confirmed
> against live events; unknown fields are preserved (`extra="allow"`). Verify with
> [`scripts/soak_userdata.py`](../concepts/assumed-shapes.md) before relying on a specific field.

## Import

Accessed as `client.user_stream`. Requires an API key ([Authentication](../getting-started/authentication.md)).

## Methods

Every `watch_*` is an async generator — iterate with `async for`; do not `await` the call itself.

### watch_orders

```python
async def watch_orders() -> AsyncIterator[ExecutionReportEvent]
```
Execution-report events as your orders change (`e=executionReport`).

```python
async with BinanceThClient() as client:
    async for evt in client.user_stream.watch_orders():
        print(evt.symbol, evt.current_order_status)
        break
```

### watch_account

```python
async def watch_account() -> AsyncIterator[OutboundAccountPositionEvent]
```
Account balance-snapshot events (`e=outboundAccountPosition`).

### watch_balances

```python
async def watch_balances() -> AsyncIterator[BalanceUpdateEvent]
```
Single balance-delta events (`e=balanceUpdate`).

### open_orders_snapshot

```python
async def open_orders_snapshot() -> list[Order]
```
A one-shot REST snapshot of currently open orders — the starting point the [`OrderTracker`](#ordertracker)
seeds from. **Returns** `list[Order]`.

### order_tracker

```python
async def order_tracker() -> OrderTracker
```
**Await it.** Returns an [`OrderTracker`](#ordertracker) — a live view of your open orders maintained from
the snapshot plus the order stream. Not yet started; call `start()`.

### aclose

```python
async def aclose() -> None
```
Stops the stream and lets the listenKeys expire. Called for you by `client.aclose()`.

---

## OrderTracker

**Available since:** 1.0.0. A live map of your open orders, seeded from `open_orders_snapshot()` and kept
current from `watch_orders()`.

### start

```python
async def start() -> None
```
Seeds the snapshot and begins consuming order events. Call once.

### synced

```python
synced: bool  # property
```
`True` once the snapshot and stream are reconciled.

### wait_synced

```python
async def wait_synced() -> None
```
Awaits until `synced` is `True`.

### open

```python
def open() -> list[Order]
```
The current open orders.

### get

```python
def get(order_id: int) -> Order | None
```
One tracked order by id, or `None`.

### aclose

```python
async def aclose() -> None
```
Stops tracking.

```python
tracker = await client.user_stream.order_tracker()
await tracker.start()
await tracker.wait_synced()
print([o.order_id for o in tracker.open()])
await tracker.aclose()
```

## See Also

- [User-data stream guide](../guides/user-data-stream.md) · [orders](orders.md)
- [Assumed shapes](../concepts/assumed-shapes.md) · [GLOBAL vs SITE](../concepts/global-vs-site.md)
