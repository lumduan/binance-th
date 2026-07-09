# ADR-0013 — Idempotency via client-order-id minting

- **Status:** Accepted
- **Date:** 2026-07-09
- **Governs:** FR-ORD-01, FR-ORD-02 · WBS-M4-02

## Context

The UNKNOWN-reconciliation guarantee in
[ADR-0006](./ADR-0006-error-taxonomy-and-5xx-unknown-reconciliation.md) — "after a 5xx on POST
`/order`, query by client order id instead of resubmitting" — is **impossible unless a client order
id exists before the request is sent**. If the caller omits `newClientOrderId`, only the server
assigns an id, which is precisely the value we cannot learn when the response is lost. Phase-1 already
carries the field and documents the intent that it is *auto-generated if not provided*
(`binance_th/models/orders.py:148-152`).

## Decision

**We will mint a collision-resistant `newClientOrderId` whenever the caller omits one**, before
signing and sending, and **return it to the caller** on the response. The minted id is a bounded,
prefixed token (a short library prefix + a monotonic/time component + a random component) that stays
within the exchange's allowed character set and length. A caller-supplied id is used verbatim.

Falsifiable: a `create_order(...)` with no id still sends a `newClientOrderId` and the returned
`Order.client_order_id` echoes it; two rapid orders receive distinct ids; a caller-provided id is
passed through unchanged.

## Consequences

**Positive**

- Every mutating request becomes reconcilable, unlocking ADR-0006's no-duplicate guarantee.
- Callers get a stable handle to their order immediately, before the server round-trip completes.

**Negative / trade-offs accepted**

- The library owns id generation and must respect the exchange's length/charset limits (⚠ ASSUMED —
  verified at implementation); a bad generator could collide or be rejected. Mitigated by tests on
  format, length, and uniqueness.

## Alternatives Considered

- **Let the server assign the id** — rejected: defeats UNKNOWN reconciliation; the assigned id is lost
  exactly when the response is lost.
- **Require the caller to always pass an id** — rejected: poor ergonomics and a footgun; forgetting it
  silently disables reconciliation.
- **Use a raw UUID** — rejected unless it fits the exchange charset/length; a prefixed compact token is
  friendlier in logs and dashboards.
