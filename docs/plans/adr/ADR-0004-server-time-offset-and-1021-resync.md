# ADR-0004 — Server-time offset manager and `-1021` resync

- **Status:** Accepted
- **Date:** 2026-07-09
- **Governs:** FR-AUTH-02, FR-GEN-03 · WBS-M1-06

## Context

Every SIGNED request carries a millisecond `timestamp`, and the server rejects any request whose
`timestamp` falls outside `recvWindow` of **server** time with error
`-1021 Timestamp for this request is outside of the recvWindow` (⚠ ASSUMED code, consistent with
Binance global and the Phase-1 `BinanceThAuthError` docstring). Client clocks drift — a laptop a few
seconds fast will have every signed call rejected. The config already exposes `recv_window`
(default 5000 ms, `le=60000`; `binance_th/config.py:99-104`) and a `ServerTime` model wraps
`GET /api/v1/time` (`binance_th/models/base.py:53-59`), but nothing computes or applies an offset.

## Decision

**We will maintain a server-time offset and add it to every signed timestamp.** On client start (and
on a periodic refresh) we call `GET /api/v1/time`, compute `offset = serverTime − localTime`, and the
signer emits `timestamp = now_ms() + offset`. If a signed call nonetheless returns `-1021`, we
**resync once** (re-fetch server time, recompute offset) and **retry the request exactly once**; a
second `-1021` propagates as `BinanceThAuthError`. `recvWindow` remains caller-tunable for high-latency
environments.

Falsifiable: with an injected local-clock skew of +30 s, signed requests still carry an in-window
timestamp; a simulated single `-1021` triggers exactly one resync+retry, a persistent `-1021` raises.

## Consequences

**Positive**

- Robust to ordinary clock drift without operator intervention.
- Bounded, non-looping remediation (one resync+retry) avoids hammering the API on a broken clock.

**Negative / trade-offs accepted**

- One extra request on start and on refresh, and one round-trip trip-up on the first `-1021`.
- A wildly wrong or fast-drifting clock still fails on the second attempt (by design — we do not loop).

## Alternatives Considered

- **Trust the local clock, no offset** — rejected: guarantees rejections on any drifted host.
- **Widen `recvWindow` to mask drift** — rejected: weakens replay protection and only hides small
  skews; kept available as a tuning knob, not the primary mechanism.
- **Resync on a fixed timer only (no reactive `-1021` handling)** — rejected: a drift between timer
  ticks still burns requests; reactive single-retry closes the gap.
