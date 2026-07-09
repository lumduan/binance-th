# ADR-0005 — Dual-window token-bucket rate limiter

- **Status:** Accepted
- **Date:** 2026-07-09
- **Governs:** FR-RL-01, FR-RL-02, FR-RL-03 · WBS-M2-01, WBS-M2-02

## Context

Binance Thailand enforces per-IP request limits and per-account order limits. ✓ VERIFIED (2026-07-09,
live `GET /api/v1/exchangeInfo`): `rateLimits` are `REQUEST_WEIGHT` **6000 / 1 min**, `ORDERS`
**6000 / 1 min**, and `ORDERS` **1000 / 10 s** — one weight window plus two order windows; **no
`RAW_REQUESTS` window** was advertised. The server reports live usage in the `x-mbx-used-weight-1m`
header (confirmed on every response) and order usage in `X-MBX-ORDER-COUNT-*`; exceeding a limit
returns **429**, and continuing
after a 429 escalates to an IP ban **418** with a `Retry-After`. The Phase-1 layer already models the
shapes: `RateLimitType` (`REQUEST_WEIGHT`, `ORDERS`, `RAW_REQUESTS`) and `RateLimitInterval`
(`binance_th/models/enums.py:112-135`), the `RateLimit` model (`binance_th/models/base.py:73-85`),
and `BinanceThRateLimitError`/`BinanceThIPBannedError` carrying `retry_after`/`used_weight`
(`binance_th/exceptions.py:111-181`). What is missing is the pacing engine.

Because these limits can change server-side, hardcoding them is fragile — the live values above are a
snapshot, not a contract.

## Decision

**We will gate every request through a dual-window token bucket**, admitting a call only when **both**
windows have capacity, and we will **seed the window limits from `exchangeInfo.rateLimits` at startup**
rather than hardcoding them. After each response we **reconcile upward**: if a server
`X-MBX-USED-WEIGHT-*` header exceeds our local count for that window, we adopt the server value (the
server is authoritative). A separate **account-scoped order counter** enforces the `ORDERS` limit for
mutating calls. On **429/418** we **hard-stop** the affected class and sleep for `Retry-After` before
resuming (backoff per [ADR-0012](./ADR-0012-retry-and-backoff-taxonomy.md)). The limiter also tracks a
`RAW_REQUESTS` window when `exchangeInfo` advertises one.

Falsifiable: the 1001st weight-unit inside a 10 s window **delays** rather than 429s; a response whose
`X-MBX-USED-WEIGHT-1m` exceeds the local counter raises the local counter to match; a 429 with
`Retry-After: 5` pauses the class for ≥5 s.

## Consequences

**Positive**

- Proactively avoids 429/418 instead of reacting to them; protects the IP from bans.
- Self-tuning to the server's published limits and live header truth, resilient to limit changes.

**Negative / trade-offs accepted**

- A token bucket adds latency under load (calls wait for capacity) — the intended behavior.
- Header reconciliation can only correct **upward** mid-window; a burst before the first header is
  seen may still 429 once (then the hard-stop engages). Accepted.

## Alternatives Considered

- **React to 429 only, no proactive limiter** — rejected: invites 418 IP bans and unpredictable
  latency spikes.
- **Hardcode 1000/10s + 6000/60s** — rejected: unverified and change-prone; `exchangeInfo` seeding is
  authoritative and future-proof.
- **Single-window limiter** — rejected: a single window cannot satisfy two simultaneous constraints
  (a 10 s burst can pass a 60 s window yet breach the 10 s one).
