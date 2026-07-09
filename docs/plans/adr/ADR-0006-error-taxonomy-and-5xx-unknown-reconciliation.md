# ADR-0006 — Error taxonomy and 5xx order-status-UNKNOWN reconciliation

- **Status:** Accepted
- **Date:** 2026-07-09
- **Governs:** FR-ORD-02, FR-ORD-03 · WBS-M1-04, WBS-M4-04

## Context

Two failure signals coexist: the HTTP status code and the envelope `code`
([ADR-0002](./ADR-0002-response-envelope-unwrap.md)). Phase-1 already provides the typed hierarchy —
`BinanceThError → BinanceThAPIError → {RateLimit(429), IPBanned(418), WAF(403), Auth(401),
BadRequest(400), Server(5xx)}` plus `Network`/`Timeout`/`Validation`/`WebSocket` — together with
`HTTP_STATUS_MAP` and `get_exception_for_status_code()` (`binance_th/exceptions.py:399-424`).

The load-bearing subtlety is already documented in that module: **a 5xx does not mean the operation
failed** — for a mutating call the execution status is *unknown*, and the order may well have been
accepted (`binance_th/exceptions.py:256-268`). Blindly retrying a POST `/order` after a 503 risks a
**duplicate order**. What is missing is (a) a single mapping that folds envelope `code` into the
hierarchy and (b) a concrete UNKNOWN-reconciliation procedure.

## Decision

**We will route every failure through one mapping** of `(HTTP status, envelope code) → typed
exception`, extending the existing `HTTP_STATUS_MAP` with envelope-`code` cases (e.g. `-1021` →
`Auth`, `-1013`/filter failures → `BadRequest`/`Validation`). **For mutating calls** (order
create/cancel), a 5xx or network timeout is surfaced as **UNKNOWN** and **reconciled by querying the
order by its `newClientOrderId`** ([ADR-0013](./ADR-0013-idempotency-and-client-order-id.md)) — never
blind-retried. If the query shows the order exists, we return it; if not, the caller may safely resubmit.
Non-mutating transient failures follow the retry policy
([ADR-0012](./ADR-0012-retry-and-backoff-taxonomy.md)).

Falsifiable: a simulated 503 on POST `/order` triggers a query-by-`clientOrderId` and produces **no
second create**; an envelope `code=-1021` raises `BinanceThAuthError`, not a generic error.

## Consequences

**Positive**

- One place decides "what kind of error is this?", reused by transport, limiter, and clients.
- Eliminates the duplicate-order class of bug at the library level.

**Negative / trade-offs accepted**

- Reconciliation costs an extra query round-trip on the (rare) mutating-call 5xx, and **requires** a
  client order id to exist before send — hence [ADR-0013](./ADR-0013-idempotency-and-client-order-id.md)
  mints one when the caller omits it.

## Alternatives Considered

- **Treat 5xx as failure and retry** — rejected: duplicate orders; contradicts the documented
  "execution status unknown" rule.
- **Treat 5xx as success** — rejected: equally wrong; the order may not exist.
- **Map on HTTP status only** — rejected: loses application-level `code`s (e.g. `-1021`, filter
  rejections) that share a 400 but need different handling.
