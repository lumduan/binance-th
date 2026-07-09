# ADR-0008 — listenKey lifecycle and pluggable manager

- **Status:** Accepted
- **Date:** 2026-07-09
- **Governs:** FR-UDS-01, FR-UDS-03 · WBS-M6-01

## Context

The user-data stream (order updates, balance changes, `executionReport`) is authenticated by a
**listenKey**: obtained via `POST /api/v1/listenKey`, kept alive with a `PUT` at least every **30
minutes**, and closed with `DELETE`. Phase-1 models the key and its scope
(`ListenKey.listen_key`, `ListenKey.symbol_type` GLOBAL/SITE; `binance_th/models/account.py:191-201`)
but has no lifecycle manager.

Two uncertainties shape the design. ⚠ ASSUMED (verify at implementation): (1) the WebSocket host path
seen in the docs, `.../w3w/wsa/stream`, hints at a **WSA (WebSocket-API)** session-auth variant that
may authenticate the user-data stream **without** a REST listenKey; (2) on a stream drop, events
emitted during the gap are lost, so local order state can silently diverge from the exchange.

## Decision

**We will drive user-data auth through `POST/PUT/DELETE /api/v1/listenKey` behind an injectable
`ListenKeyManager` interface**, so an alternative (WSA-native) manager can slot in later **without
changing callers**. The manager schedules keepalive strictly **under 30 minutes**, `DELETE`s the key
on clean shutdown, and on a **drop/reconnect reconciles local state against REST truth** — re-reading
`openOrders` and recent `userTrades` and replacing the local view — rather than trusting that no
events were missed.

Falsifiable: keepalive fires at < 30 min; the manager is an interface with the REST implementation as
one impl (a fake impl passes the same tests); after a simulated drop, local order state equals the
REST `openOrders`+`userTrades` reconstruction.

## Consequences

**Positive**

- The WSA-vs-REST question is deferred behind a seam instead of blocking user-data work now.
- Drop reconciliation makes the stream **self-healing**; local state converges to exchange truth.

**Negative / trade-offs accepted**

- Reconciliation costs two REST reads per reconnect and briefly leans on the rate budget
  ([ADR-0005](./ADR-0005-dual-window-rate-limiter.md)).
- Maintaining an interface for a second implementation that may never ship is mild over-engineering —
  accepted because the WSA path is plausible and the interface is cheap.

## Alternatives Considered

- **Hardcode the REST listenKey flow** — rejected: if TH uses WSA-native auth, this is a rewrite of
  the user-data client rather than a swapped manager.
- **Reconnect and resume without reconciliation** — rejected: missed events during the gap leave the
  local book/orders wrong with no signal.
- **Keepalive on a 30-min timer exactly** — rejected: no margin; clock jitter or a slow `PUT` lets the
  key expire. We keepalive well under the limit.
