# Architecture overview

[Home](../index.md) > Architecture > Overview

How `binance-th` is layered, and where each design decision is recorded. This page is a map — the depth
lives in the [HLD](../plans/hld.md), [FRD](../plans/frd.md), [WBS](../plans/wbs.md), and the
[ADRs](../plans/adr/README.md).

## Layers

```text
BinanceThClient                        facade: owns config, transport, and the sub-clients; lifecycle
│
├── MarketClient  AccountClient        REST resource clients — build params, parse typed responses
│   WalletClient  OrdersClient
│        │
│        └── Transport                 one async pipeline for every REST call:
│              signing ─ timesync ─ rate limiter ─ retry ─ envelope unwrap ─ error mapping ─ httpx
│
├── StreamClient                       WebSocket market streams (per-host connections)
│     └── ManagedOrderBook             REST snapshot + depth-diff → a self-syncing local book
│
└── UserDataStream                     user-data stream (api-key + listenKey lifecycle)
      └── OrderTracker                 open-orders snapshot + executionReport → a live order view
```

## The REST request lifecycle

Every REST call goes through `Transport.request(...)`. For a **signed** endpoint:

1. The resource client builds business params (validated by a `RequestModel` where one applies).
2. Orders additionally run [local pre-trade validation](../plans/adr/ADR-0009-local-pre-trade-validation.md).
3. Transport attaches `timestamp = now_ms + server_time_offset` and signs the ordered query string with
   HMAC-SHA256 ([signing](../plans/adr/ADR-0003-request-signing-and-param-ordering.md),
   [time sync](../plans/adr/ADR-0004-server-time-offset-and-1021-resync.md)).
4. The [dual-window rate limiter](../plans/adr/ADR-0005-dual-window-rate-limiter.md) reserves request
   weight before sending.
5. `httpx` sends the request; transient failures are retried on a
   [backoff taxonomy](../plans/adr/ADR-0012-retry-and-backoff-taxonomy.md).
6. The [response envelope](../plans/adr/ADR-0002-response-envelope-unwrap.md) `{code, msg, data}` is
   unwrapped to `data` (unless the endpoint is bare).
7. Non-2xx responses map to a [typed exception](../plans/adr/ADR-0006-error-taxonomy-and-5xx-unknown-reconciliation.md).
   A 5xx/timeout on an order create triggers **reconciliation** — see
   [Errors & reconciliation](../concepts/errors-and-reconciliation.md).
8. The payload is parsed into a `ResponseModel` (`extra="allow"`).

Secrets never reach logs — see [secret redaction](../plans/adr/ADR-0017-secret-redaction-and-logging.md).

## WebSockets

Market streams use a [dual-host topology](../plans/adr/ADR-0014-stream-routing-and-base-url-topology.md)
(GLOBAL on `/gstream`, SITE on `/nstream`), reconnecting automatically. The user-data stream manages
[listenKey lifecycle](../plans/adr/ADR-0008-listenkey-lifecycle-and-manager.md) with per-symbol-type keys.
See [WebSockets](../concepts/websockets.md) and [GLOBAL vs SITE](../concepts/global-vs-site.md).

## Decision records

The full set of ADRs (in [`docs/plans/adr/`](../plans/adr/README.md)):

| # | Decision | Subsystem |
|---|----------|-----------|
| [0001](../plans/adr/ADR-0001-async-core-stack.md) | Async core stack (`httpx` + `websockets`) | transport |
| [0002](../plans/adr/ADR-0002-response-envelope-unwrap.md) | Response envelope unwrap | transport |
| [0003](../plans/adr/ADR-0003-request-signing-and-param-ordering.md) | Request signing + param ordering | signing |
| [0004](../plans/adr/ADR-0004-server-time-offset-and-1021-resync.md) | Server-time offset + `-1021` resync | time sync |
| [0005](../plans/adr/ADR-0005-dual-window-rate-limiter.md) | Dual-window rate limiter | rate limiting |
| [0006](../plans/adr/ADR-0006-error-taxonomy-and-5xx-unknown-reconciliation.md) | Error taxonomy + 5xx-UNKNOWN reconciliation | errors |
| [0007](../plans/adr/ADR-0007-local-order-book-sync.md) | Local order-book sync | order book |
| [0008](../plans/adr/ADR-0008-listenkey-lifecycle-and-manager.md) | listenKey lifecycle + manager | user stream |
| [0009](../plans/adr/ADR-0009-local-pre-trade-validation.md) | Local pre-trade validation | orders |
| [0010](../plans/adr/ADR-0010-packaging-and-distribution.md) | Packaging + distribution | build/release |
| [0011](../plans/adr/ADR-0011-global-vs-site-symbol-handling.md) | GLOBAL vs SITE symbol handling | symbols |
| [0012](../plans/adr/ADR-0012-retry-and-backoff-taxonomy.md) | Retry + backoff taxonomy | retry |
| [0013](../plans/adr/ADR-0013-idempotency-and-client-order-id.md) | Idempotency + client order id | orders |
| [0014](../plans/adr/ADR-0014-stream-routing-and-base-url-topology.md) | Stream routing + base-URL topology | streams |
| [0015](../plans/adr/ADR-0015-connection-session-lifecycle-and-pooling.md) | Connection/session lifecycle + pooling | transport |
| [0016](../plans/adr/ADR-0016-pagination-and-time-window-iteration.md) | Pagination + time-window iteration | pagination |
| [0017](../plans/adr/ADR-0017-secret-redaction-and-logging.md) | Secret redaction + logging | logging |

## See Also

- [HLD](../plans/hld.md) · [FRD](../plans/frd.md) · [WBS](../plans/wbs.md) · [Roadmap](../plans/ROADMAP.md)
- [Concepts](../concepts/global-vs-site.md) · [Reference](../reference/index.md)
