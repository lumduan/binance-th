# ADR-0012 — Retry and backoff taxonomy

- **Status:** Accepted
- **Date:** 2026-07-09
- **Governs:** FR-RL-03 · WBS-M2-03

## Context

The config exposes `max_retries` (default 3; `binance_th/config.py:90-94`) but nothing defines
**which** failures are retryable or on **what schedule**. Without a single policy, retries get
sprinkled ad hoc across layers, and — most dangerously — a naive "retry everything" would resubmit
mutating order calls, causing duplicates (the exact hazard
[ADR-0006](./ADR-0006-error-taxonomy-and-5xx-unknown-reconciliation.md) exists to prevent). The
limiter ([ADR-0005](./ADR-0005-dual-window-rate-limiter.md)) also needs a shared backoff for `Retry-After`
sleeps rather than inventing its own.

## Decision

**We will retry only transient, non-mutating failures, on jittered exponential backoff, up to
`max_retries`.** Retryable: connection errors, timeouts, 5xx on **read** (non-mutating) endpoints, and
429/418 (after honoring `Retry-After`). The schedule is exponential with full jitter — base ≈ 0.5 s,
factor ×2, cap ≈ 8 s — shared by the transport and the limiter. **Mutating** calls (order
create/cancel) are **never auto-retried**; their 5xx/timeout goes to UNKNOWN reconciliation
([ADR-0006](./ADR-0006-error-taxonomy-and-5xx-unknown-reconciliation.md)).

Falsifiable: a mutating call that times out is **not** re-sent (it reconciles); a read call that 503s
retries with increasing, jittered delays and gives up after `max_retries`; a 429 waits ≥ `Retry-After`
before the next attempt.

## Consequences

**Positive**

- One backoff implementation, reused; predictable, bounded retry behavior.
- Jitter avoids synchronized retry storms across concurrent calls.

**Negative / trade-offs accepted**

- Non-mutating retries can mask a persistent server issue as latency until `max_retries` is exhausted.
- Excluding mutating calls means a transient blip on an order surfaces to the caller (as a reconciled
  result) rather than being silently retried — the safe choice.

## Alternatives Considered

- **Retry all failures uniformly** — rejected: duplicates orders.
- **Fixed-interval retries** — rejected: no backoff invites thundering-herd and burns the rate budget.
- **No retries (fail fast everywhere)** — rejected: ordinary transient network blips would surface as
  hard errors for read paths that can safely retry.
