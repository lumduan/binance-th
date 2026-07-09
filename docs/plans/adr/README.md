# Architecture Decision Records — `binance-th`

Each ADR records **one** accepted, load-bearing decision and is **immutable**: to change a decision,
write a new ADR and set the old one's `Status` to `Superseded by ADR-00XX`. Files follow
`ADR-00NN-kebab-slug.md` (4-digit, zero-padded, monotonically increasing, never renumbered), using the
[ADR-0000 template](./ADR-0000-template.md). Every ADR's metadata block carries a `**Governs:**` line
linking the FR-IDs ([frd.md](../frd.md)) and WBS-IDs ([wbs.md](../wbs.md)) it drives, so the
decision ⇄ requirement ⇄ work-item spine is greppable in both directions.

> This standalone index is an **addition** over the `opendys` convention (which surfaces ADRs inline in
> its ROADMAP); it is included here per the project's planning brief.

| # | Title | Status | Governs (primary FRs) |
|---|-------|--------|-----------------------|
| [0001](./ADR-0001-async-core-stack.md) | Async-only core stack (httpx + websockets + Pydantic v2 + Decimal) | Accepted | FR-GEN-01 |
| [0002](./ADR-0002-response-envelope-unwrap.md) | Centralized response-envelope unwrapping | Accepted | FR-MKT-01, FR-ACC-01 |
| [0003](./ADR-0003-request-signing-and-param-ordering.md) | Request signing and parameter ordering (HMAC-SHA256) | Accepted | FR-AUTH-01 |
| [0004](./ADR-0004-server-time-offset-and-1021-resync.md) | Server-time offset manager and `-1021` resync | Accepted | FR-AUTH-02, FR-GEN-03 |
| [0005](./ADR-0005-dual-window-rate-limiter.md) | Dual-window token-bucket rate limiter | Accepted | FR-RL-01, FR-RL-02, FR-RL-03 |
| [0006](./ADR-0006-error-taxonomy-and-5xx-unknown-reconciliation.md) | Error taxonomy and 5xx order-status-UNKNOWN reconciliation | Accepted | FR-ORD-02, FR-ORD-03 |
| [0007](./ADR-0007-local-order-book-sync.md) | Local order-book (depth) synchronization | Accepted | FR-WSS-02 |
| [0008](./ADR-0008-listenkey-lifecycle-and-manager.md) | listenKey lifecycle and pluggable manager | Accepted | FR-UDS-01, FR-UDS-03 |
| [0009](./ADR-0009-local-pre-trade-validation.md) | Local pre-trade validation against symbol filters | Accepted | FR-ORD-01, FR-MKT-03 |
| [0010](./ADR-0010-packaging-and-distribution.md) | Packaging and distribution | Accepted | FR-GEN-04 |
| [0011](./ADR-0011-global-vs-site-symbol-handling.md) | GLOBAL vs SITE symbol-type handling | Accepted | FR-WSS-03, FR-MKT-03 |
| [0012](./ADR-0012-retry-and-backoff-taxonomy.md) | Retry and backoff taxonomy | Accepted | FR-RL-03 |
| [0013](./ADR-0013-idempotency-and-client-order-id.md) | Idempotency via client-order-id minting | Accepted | FR-ORD-01, FR-ORD-02 |
| [0014](./ADR-0014-stream-routing-and-base-url-topology.md) | Stream routing and base-URL topology | Accepted | FR-WSS-01, FR-WSS-03 |
| [0015](./ADR-0015-connection-session-lifecycle-and-pooling.md) | Connection/session lifecycle and pooling | Accepted | FR-GEN-01, FR-WSS-01 |
| [0016](./ADR-0016-pagination-and-time-window-iteration.md) | Pagination and time-window iteration | Accepted | FR-MKT-02, FR-ACC-02, FR-WAL-02 |
| [0017](./ADR-0017-secret-redaction-and-logging.md) | Secret redaction and logging policy | Accepted | FR-AUTH-03 |
| [template](./ADR-0000-template.md) | ADR template | — | — |

**Reading order for implementers:** transport/auth core (0001–0004, 0015, 0017) → limiting/errors
(0005, 0006, 0012) → REST resources (0002, 0009, 0011, 0013, 0016) → streaming (0007, 0008, 0014) →
packaging (0010). See [ROADMAP.md](../ROADMAP.md) for how these map onto milestones.
