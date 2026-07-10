# WebSockets

[Home](../index.md) > Concepts > WebSockets

**English** · [ไทย](../th/concepts/websockets.md)

Both `client.ws` (market streams) and `client.user_stream` (user data) run over WebSocket. The library
handles connection lifecycle, routing, reconnection, and keepalive so you can just iterate over events.

## One connection per host, opened lazily

The client opens a WebSocket only when you first subscribe, and multiplexes streams over it. Because
GLOBAL and SITE symbols live on different hosts (see [GLOBAL vs SITE](global-vs-site.md)), watching both
types opens one connection each — keyed by host, invisible to you.

## Reconnection is automatic

If a socket drops, the supervisor reconnects with capped exponential backoff and re-subscribes your
streams. It also reconnects **proactively** shortly before the exchange's ~24-hour connection cap — a
planned reconnect, not an error. During any gap the local order book re-snapshots itself, so you never
see stale data silently.

Turn it off with `BinanceThConfig(ws_auto_reconnect=False)` — then a drop surfaces as a
`BinanceThWebSocketError` on the stream.

## Keepalive

For market streams, keepalive is the WebSocket ping handled by the `websockets` library
(`ws_ping_interval` / `ws_ping_timeout`). For the user-data stream there's an extra, separate keepalive:
the `listenKey` must be refreshed with a REST `PUT` well under 30 minutes, which the client schedules for
you (`user_stream_keepalive_interval`, default 1200 s).

## Backpressure

Each subscription has a bounded queue with a drop-oldest policy, so one slow consumer can never stall
the shared reader for other streams. If you fall behind, you drop the oldest events, not the newest.

## Clean shutdown

Exiting `async with BinanceThClient()` (or calling `client.aclose()`) cancels the background tasks,
closes the sockets, and — for the user-data stream — deletes the `listenKey`. Managed objects returned by
the WS layer (`ManagedOrderBook`, `OrderTracker`) also have their own `await aclose()` if you want to
stop one early.

## See Also

- [Market streams guide](../guides/market-streams.md)
- [Local order book guide](../guides/local-order-book.md)
- [User-data stream guide](../guides/user-data-stream.md)
