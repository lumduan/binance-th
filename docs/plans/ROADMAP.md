# ROADMAP — `binance-th`

The master phased plan and status index. Milestones map to **semver** targets; each milestone lists
its hard dependencies and the ADRs it needs. Task-level decomposition lives in [wbs.md](./wbs.md);
requirements in [frd.md](./frd.md); decisions in [adr/](./adr/README.md).

## Status legend

| Mark | Meaning |
| --- | --- |
| `[ ]` | Not started |
| `[~]` | In progress |
| `[x]` | Complete |
| `[-]` | Skipped / deferred |

## Milestones → semver

| Milestone | semver | Scope | Hard deps | ADRs needed |
|-----------|--------|-------|-----------|-------------|
| **M0** Planning suite | `0.1.0` | This `docs/plans/` suite, `.claude` project-skill, bilingual README | — | all (authoring) |
| **M1** Transport & Auth core | `0.2.0` | `httpx` transport, envelope unwrap, HMAC signer, server-time offset, error-taxonomy wiring, session lifecycle, secret redaction | M0 | 0001, 0002, 0003, 0004, 0006, 0015, 0017 |
| **M2** Rate limiting | `0.3.0` | Dual-window token bucket, header reconciliation, order counter, retry/backoff | M1 | 0005, 0012 |
| **M3** REST: market + account/wallet read | `0.4.0` | Market clients (bare payloads), `accountV2`, wallet/fiat reads, `exchangeInfo`/`executionRules` cache, pagination | M1 (M2 for throughput) | 0002, 0011, 0016 |
| **M4** Orders | `0.5.0` | create / cancel / query, pre-trade validation, client-id minting, UNKNOWN reconciliation | M1, M2, M3 | 0003, 0006, 0009, 0013 |
| **M5** WS market streams + order book | `0.6.0` | WS client, `?streams=` multiplex, GLOBAL/SITE routing, local order-book sync | M1 (M3 for depth snapshot) | 0007, 0011, 0014, 0015 |
| **M6** User-data stream | `0.7.0` | listenKey manager, event decode, drop reconciliation | M4, M5 | 0002, 0008, 0015 |
| **M7** Hardening & release | `1.0.0` | `bandit`/`pip-audit` + `security.yml`, `docker-publish.yml`, `LICENSE`, docs, coverage gate | M1–M6 | 0005, 0010, 0017 |

**Critical path:** `M0 → M1 → M2 → M3 → M4 → M6 → M7`. Orders (M4) cannot ship until signing +
time-offset + envelope + errors (M1) and the limiter (M2) exist, and cannot be *trusted* until
`exchangeInfo`/`executionRules` (M3) feed pre-trade validation; user-data (M6) additionally waits on
orders (M4) for reconciliation, so that chain is longer than the parallel WS branch
(`… M1 → M3 → M5 → M6`).

## Current status

- [x] **M0** — Planning suite (HLD, FRD, WBS, ROADMAP, 17 ADRs, project-skill, bilingual README)
- [x] **M1** — Transport & Auth core
- [x] **M2** — Rate limiting
- [x] **M3** — REST market + account/wallet read
- [x] **M4** — Orders (`client.orders`: create/cancel/query/openOrders + validation + id-minting + UNKNOWN reconciliation; mock-only, live placement pending a supervised soak)
- [x] **M5** — WS market streams + order book (`client.ws`: watch_* async iterators for depth/trade/aggTrade/kline/bookTicker/ticker + self-syncing `order_book`; dual-host GLOBAL/SITE routing and shapes **live-verified 2026-07-09** — the ADR-0014 single-host default was flipped to dual-host)
- [ ] **M6** — User-data stream
- [ ] **M7** — Hardening & release
- [x] **Phase 1 (pre-M0)** — models, exceptions, config (already in `main`)

## ADRs (all authored in M0)

- [x] `ADR-0001` — Async-only core stack
- [x] `ADR-0002` — Response-envelope unwrap
- [x] `ADR-0003` — Request signing & param ordering
- [x] `ADR-0004` — Server-time offset & `-1021` resync
- [x] `ADR-0005` — Dual-window rate limiter
- [x] `ADR-0006` — Error taxonomy & 5xx-UNKNOWN reconciliation
- [x] `ADR-0007` — Local order-book sync
- [x] `ADR-0008` — listenKey lifecycle & manager
- [x] `ADR-0009` — Local pre-trade validation
- [x] `ADR-0010` — Packaging & distribution
- [x] `ADR-0011` — GLOBAL vs SITE handling
- [x] `ADR-0012` — Retry & backoff taxonomy
- [x] `ADR-0013` — Idempotency & client-order-id
- [x] `ADR-0014` — Stream routing & base-URL topology
- [x] `ADR-0015` — Connection/session lifecycle & pooling
- [x] `ADR-0016` — Pagination & time-window iteration
- [x] `ADR-0017` — Secret redaction & logging

> Note: the `0.1.0` target currently used by `pyproject.toml` covers Phase-1 code; M0 is documentation
> only. Version bumps begin at M1 (`0.2.0`).
