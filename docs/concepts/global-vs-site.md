# GLOBAL vs SITE symbols

[Home](../index.md) > Concepts > GLOBAL vs SITE

**English** · [ไทย](../th/concepts/global-vs-site.md)

Binance Thailand lists two kinds of trading symbols, and knowing which is which explains a few things
that would otherwise look inconsistent.

- **GLOBAL** — shared with the main Binance platform (e.g. `BTCUSDT`).
- **SITE** — region-specific to Thailand (e.g. `BTCTHB`).

They are exposed as the `SymbolType` enum (`SymbolType.GLOBAL` / `SymbolType.SITE`).

## Why it matters

**They don't always carry the same fields.** Binance Thailand makes no parity promise between the two,
so some model fields are `Optional` simply because they only appear for one type — for example, a
`depthUpdate` from a SITE symbol carries `T`/`pu` that a GLOBAL one doesn't; `trade`/`aggTrade` from a
GLOBAL symbol carry an `M` flag a SITE one doesn't; several `Ticker24hr` and `Trade` fields are `null`
on SITE symbols.

**Their WebSocket streams live on different hosts.** GLOBAL streams come from `ws_base_url_global`
(`/gstream`), SITE from `ws_base_url_site` (`/nstream`). The library resolves a symbol's type and routes
the connection for you — you just pass the symbol. Watching one GLOBAL and one SITE symbol simply opens
two connections under the hood.

**A few endpoints are GLOBAL-only.** `client.market.reference_price(...)` and
`client.market.execution_rules()` exist only for GLOBAL symbols; calling them for a SITE/THB symbol
returns a `400` (`BinanceThBadRequestError`).

## Check a symbol's type

```python
async with BinanceThClient() as client:
    types = await client.symbol_types(symbol="BTCTHB")
    print(types[0].symbol, types[0].symbol_type)   # BTCTHB SymbolType.SITE
```

`client.symbol_types()` (no argument) returns the full list.

## The user-data stream

The user-data stream is also split: `POST /api/v1/listenKey` returns **one key per type** (a Thailand
specific behaviour), so the client keeps one connection per type behind the scenes. You don't manage
that — `client.user_stream.*` aggregates events from both. See the
[user-data stream guide](../guides/user-data-stream.md).

## See Also

- [WebSockets](websockets.md) — how connections and routing work
- [Assumed shapes](assumed-shapes.md) — why some fields are provisional
- [Market data guide](../guides/market-data.md)
