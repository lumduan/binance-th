# ADR-0015 — Connection/session lifecycle and pooling

- **Status:** Accepted
- **Date:** 2026-07-09
- **Governs:** FR-GEN-01, FR-WSS-01 · WBS-M1-01, WBS-M5-01

## Context

Creating an `httpx.AsyncClient` or a WebSocket connection per call is wasteful (no connection reuse,
TLS re-handshakes) and leaks sockets — the classic "unclosed connector" warning. Long-lived streams
add two exchange-imposed limits that must be respected: a connection is force-closed at ~**24 hours**,
and a single connection accepts a bounded number of streams (~**1024**) (⚠ ASSUMED — verify at
implementation). Phase-1 config already anticipates this with `ws_auto_reconnect`, `ws_ping_interval`,
and `ws_ping_timeout` (`binance_th/config.py:107-120`) but there is no owning lifecycle.

## Decision

**We will own one `httpx.AsyncClient` and one multiplexed WebSocket connection per client instance**,
expose the client as an **async context manager** (`async with BinanceThClient(cfg) as c:`) that
**closes both deterministically** on exit, **proactively reconnect** the WebSocket shortly before the
24-hour cap (a planned reconnect, **not** an error — consistent with
`BinanceThWebSocketError`'s docstring, `exceptions.py:372-383`), and **cap subscriptions** at the
documented per-connection limit, opening an additional connection only if needed.

Falsifiable: exiting the `async with` block issues no "unclosed connector"/"unclosed transport"
warning; a forced 24 h boundary reconnects without surfacing an error to the caller; subscribing past
the per-connection cap allocates a second connection rather than failing.

## Consequences

**Positive**

- Connection reuse (pooling, HTTP/2 multiplexing) and deterministic teardown; no socket leaks.
- The 24 h and stream-count limits are handled centrally, invisibly to callers.

**Negative / trade-offs accepted**

- The client becomes a stateful, must-close resource; callers must use the context manager (or call
  `aclose()`), which is the standard async-resource contract.

## Live verification (M5 · 2026-07-09)

The topology probe ([ADR-0014](./ADR-0014-stream-routing-and-base-url-topology.md)) established that
GLOBAL and SITE symbols stream from **different hosts** (`/gstream` vs `/nstream`). So "one
multiplexed WebSocket per client instance" is refined to **one multiplexed connection _per host_**:
a client watching only one symbol type holds a single connection; one watching both holds two (a
GLOBAL host connection + a SITE host connection). `StreamClient` keys connections by host and applies
the proactive-reconnect + per-connection stream-cap machinery to each independently — the lifecycle
guarantees (deterministic close, no leaks, planned pre-24h reconnect) are unchanged and hold per
connection. The per-connection stream cap (~1024) and the ~24h boundary remain ⚠ ASSUMED (v1 ships a
single connection per host with a proactive-reconnect timer; multi-connection spill past the cap is
the flagged trim point).

## Alternatives Considered

- **New client/connection per request** — rejected: no reuse, socket churn, leaks.
- **Global shared singletons** — rejected: hidden global state, impossible to run two configs (e.g.
  two API keys) in one process, and unclear ownership of teardown.
- **Reconnect only reactively on the 24 h close** — rejected: a reactive reconnect drops messages at
  the boundary; a proactive one overlaps cleanly.
