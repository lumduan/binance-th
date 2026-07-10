# User-data stream

[Home](../index.md) > Guides > User-data stream

**English** · [ไทย](../th/guides/user-data-stream.md)

`client.user_stream` delivers your own account activity in real time — order updates, balance snapshots,
and balance deltas — plus a self-healing view of your open orders.

## Prerequisites

- [Authentication](../getting-started/authentication.md) — needs `api_key` (no HMAC secret required for
  the listenKey)
- [WebSockets](../concepts/websockets.md)

> ⚠ The user-data **event** models are ⚠ASSUMED (the connection is verified, but no live event was
> captured on an idle account). See [Assumed shapes](../concepts/assumed-shapes.md).

---

## The order tracker (recommended)

The easiest way to follow your orders is `order_tracker()` — a live view that seeds from
`openOrders`, updates from every `executionReport`, and re-reads REST truth whenever the socket drops.

```python
async with BinanceThClient() as client:
    tracker = await client.user_stream.order_tracker()
    await tracker.wait_synced()
    print(tracker.open())                 # list[Order], kept current
    print(tracker.get(12345))             # one order by id, or None
    ...
    await tracker.aclose()
```

## Raw event streams

If you'd rather handle events yourself:

| Method | Yields | Event |
|--------|--------|-------|
| `client.user_stream.watch_orders()` | `ExecutionReportEvent` | order created/filled/canceled |
| `client.user_stream.watch_account()` | `OutboundAccountPositionEvent` | balance snapshot after a change |
| `client.user_stream.watch_balances()` | `BalanceUpdateEvent` | a deposit/withdrawal/transfer delta |

```python
async for report in client.user_stream.watch_orders():
    print(report.symbol, report.order_id, report.current_order_status, report.cumulative_filled_qty)
```

Order events from **both** GLOBAL and SITE symbols arrive on the same iterator — the split is handled
for you.

## Lifecycle, handled for you

Under the hood the client creates the listenKey(s) — Binance Thailand returns **one per symbol type** —
keeps them alive with periodic REST `PUT`s, and deletes them on close. You never touch the listenKey.
(The SITE key is too long for the exchange's own keepalive endpoint, so it can't be extended and simply
self-heals via reconnect — again, invisible to you.)

Leaving the `async with` (or `await tracker.aclose()`) cleans everything up.

## See Also

- [Orders guide](orders.md)
- [Assumed shapes](../concepts/assumed-shapes.md) — and `scripts/soak_userdata.py` to verify event shapes
- [Reference: user-stream](../reference/user-stream.md)
