# binance-th documentation

A typed, async Python client for the Binance **Thailand** API — REST + WebSocket.

```python
import asyncio
from binance_th import BinanceThClient

async def main() -> None:
    async with BinanceThClient() as client:
        book = await client.market.depth("BTCTHB", limit=5)
        print(book.bids[0], book.asks[0])

asyncio.run(main())
```

## Learning paths

**New to binance-th?**

1. [Installation](getting-started/installation.md)
2. [Quickstart](getting-started/quickstart.md)
3. [Authentication](getting-started/authentication.md) — for signed calls and the user-data stream
4. Pick a [guide](guides/market-data.md)

**Comfortable with async Python?** Jump straight to the [API reference](reference/index.md), or read
[`llms.txt`](../llms.txt) for the whole surface on one page.

---

## Getting started 🚀

*Install it and make your first calls.*

- [Installation](getting-started/installation.md) — uv / pip, Python 3.12+
- [Quickstart](getting-started/quickstart.md) — a first end-to-end script
- [Authentication](getting-started/authentication.md) — credentials, env vars, which calls need them

## Concepts 💡

*The handful of ideas that make the rest click.*

- [GLOBAL vs SITE symbols](concepts/global-vs-site.md) — the Thailand-specific symbol split
- [Money & Decimals](concepts/money-and-decimals.md) — why everything is `Decimal`
- [Errors & reconciliation](concepts/errors-and-reconciliation.md) — the exception tree and the "5xx is unknown" rule
- [Rate limiting](concepts/rate-limiting.md) — the dual-window limiter and header reconciliation
- [WebSockets](concepts/websockets.md) — connections, reconnection, keepalive
- [Assumed shapes](concepts/assumed-shapes.md) — which response models are not yet live-verified

## Guides 📘

*Task-oriented, with complete runnable examples.*

- [Market data](guides/market-data.md) — depth, trades, klines, tickers
- [Orders](guides/orders.md) — create / cancel / query, validation, UNKNOWN reconciliation
- [Market streams](guides/market-streams.md) — the `watch_*` async iterators
- [Local order book](guides/local-order-book.md) — a self-syncing book
- [User-data stream](guides/user-data-stream.md) — order/balance events + the order tracker
- [Pagination](guides/pagination.md) — the `iter_*` helpers

## Reference 📖

*Exact signatures — spec, not tutorial.*

- [API reference](reference/index.md) — the package tree, capabilities, and per-namespace pages

## Architecture 🏛️

*How it's built and why.*

- [Overview](architecture/overview.md) — the layering
- [Architecture Decision Records](plans/adr/README.md) — the 17 ADRs behind the design

## Development 🛠️

*Contribute or release.*

- [Contributing](development/contributing.md)
- [Release process](development/release-process.md)
- [Testing](development/testing.md)

## Community 🌍

- [Changelog](../CHANGELOG.md) · [Security policy](../SECURITY.md) ·
  [Code of Conduct](../CODE_OF_CONDUCT.md)
- Issues & questions: <https://github.com/lumduan/binance-th/issues>
