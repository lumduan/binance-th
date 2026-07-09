# Work Breakdown Structure — `binance-th`

Milestones ([ROADMAP.md](./ROADMAP.md)) decomposed into work items. Each item:
`WBS-Mn-NN | Title | Deps | ADRs | FRs | Size (S/M/L) | Exit criteria`. Sizes are relative effort, not
time. Items are the unit of PR; exit criteria are testable.

## M0 — Planning suite (`0.1.0`, docs only)

| ID | Title | Deps | ADRs | FRs | Sz | Exit criteria |
|----|-------|------|------|-----|----|---------------|
| WBS-M0-01 | Author planning suite (HLD/FRD/WBS/ROADMAP/17 ADRs/indices) | — | all | — | L | this PR merged; cross-refs resolve |
| WBS-M0-02 | `project-skill.md` + track `.claude/knowledge` in git | M0-01 | 0017 | — | S | file tracked; `settings.local.json` still ignored |
| WBS-M0-03 | Bilingual README + planning/ADR index | M0-01 | 0010 | FR-GEN-04 | S | both language anchors resolve; links live |

## M1 — Transport & Auth core (`0.2.0`)

| ID | Title | Deps | ADRs | FRs | Sz | Exit criteria |
|----|-------|------|------|-----|----|---------------|
| WBS-M1-01 | `httpx.AsyncClient` transport + session context-manager | — | 0001, 0015 | FR-GEN-01 | M | `async with` opens/closes cleanly; no unclosed-connector warning |
| WBS-M1-02 | Add `httpx` runtime dependency | — | 0001, 0010 | FR-GEN-04 | S | `pyproject` + `uv.lock` updated; `mypy --strict` clean |
| WBS-M1-03 | Envelope unwrap layer | M1-01 | 0002 | FR-MKT-01, FR-ACC-01 | M | `code!=0` raises mapped exc; bare `depth` parses; both tested |
| WBS-M1-04 | Error mapper (HTTP status × envelope code) | M1-01, M1-03 | 0006 | FR-ORD-03 | M | mapping table + tests; extends `HTTP_STATUS_MAP` |
| WBS-M1-05 | HMAC-SHA256 signer (insertion order, raw concat) | M1-01 | 0003 | FR-AUTH-01 | M | golden vector passes; param reorder changes sig |
| WBS-M1-06 | Server-time offset + `-1021` resync | M1-05 | 0004 | FR-AUTH-02, FR-GEN-03 | S | injected skew accepted; single resync+retry on `-1021` |
| WBS-M1-07 | Secret redaction in logging path | M1-01 | 0017 | FR-AUTH-03 | S | logs contain no signature/secret/listenKey |

## M2 — Rate limiting (`0.3.0`)

| ID | Title | Deps | ADRs | FRs | Sz | Exit criteria |
|----|-------|------|------|-----|----|---------------|
| WBS-M2-01 | Dual-window token bucket, seeded from `exchangeInfo` | M1-01 | 0005 | FR-RL-01 | L | 1001st weight/10 s **delays**, not 429 |
| WBS-M2-02 | Header reconciliation + account order counter | M2-01 | 0005 | FR-RL-02, FR-RL-03 | M | `X-MBX-USED-WEIGHT-*` raises local counter when higher |
| WBS-M2-03 | Retry/backoff engine (jittered exponential) | M1-04 | 0012 | FR-RL-03 | M | read 5xx retries w/ backoff; mutating excluded |

## M3 — REST: market + account/wallet read (`0.4.0`)

| ID | Title | Deps | ADRs | FRs | Sz | Exit criteria |
|----|-------|------|------|-----|----|---------------|
| WBS-M3-01 | Market clients (depth/trades/klines/tickers, bare) | M1-03 | 0002 | FR-MKT-01 | M | typed out; mocked tests; unknown fields tolerated |
| WBS-M3-02 | `accountV2` + wallet/fiat reads (signed) | M1-05, M1-06 | 0003, 0002 | FR-ACC-01, FR-WAL-01 | M | signed reads pass; balances `Decimal` |
| WBS-M3-03 | Pagination async generator | M3-01 | 0016 | FR-MKT-02, FR-ACC-02, FR-WAL-02 | M | contiguous, de-duped rows across windows |
| WBS-M3-04 | `exchangeInfo`/`executionRules` cache + `symbolType` | M1-03 | 0011, 0009 | FR-GEN-02, FR-MKT-03 | M | cached lookups; `type` + PRICE_RANGE surfaced |

## M4 — Orders (`0.5.0`)

| ID | Title | Deps | ADRs | FRs | Sz | Exit criteria |
|----|-------|------|------|-----|----|---------------|
| WBS-M4-01 | Order create/cancel/query clients (signed) | M1-05, M2-02, M3-04 | 0003, 0006 | FR-ORD-03 | M | signed order flow; id-or-clientId enforced |
| WBS-M4-02 | Client-order-id minting | M4-01 | 0013 | FR-ORD-01, FR-ORD-02 | S | minted id sent + echoed; unique; charset/length valid |
| WBS-M4-03 | Pre-trade validator (filters + PRICE_RANGE, ROUND_DOWN) | M3-04 | 0009 | FR-ORD-01, FR-MKT-03 | M | sub-tick floored; below-notional rejected locally |
| WBS-M4-04 | Order UNKNOWN reconciliation | M4-01, M4-02, M1-06 | 0006, 0013 | FR-ORD-02 | M | injected 503 → query-by-clientId, **no** duplicate |

## M5 — WS market streams + order book (`0.6.0`)

| ID | Title | Deps | ADRs | FRs | Sz | Exit criteria |
|----|-------|------|------|-----|----|---------------|
| WBS-M5-01 | WS client + stream router (`?streams=`, GLOBAL/SITE) | M1-01 | 0014, 0015 | FR-WSS-01, FR-WSS-03 | L | 2-symbol multiplex; routing is config data |
| WBS-M5-02 | Verify GLOBAL/SITE topology vs live console | M5-01 | 0011, 0014 | FR-WSS-03 | S | single-host default confirmed or flipped (config-only) |
| WBS-M5-03 | Local order-book sync engine | M5-01, M3-01 | 0007 | FR-WSS-02 | L | update-id gap → re-snapshot; replay == reference book |

## M6 — User-data stream (`0.7.0`)

| ID | Title | Deps | ADRs | FRs | Sz | Exit criteria |
|----|-------|------|------|-----|----|---------------|
| WBS-M6-01 | `ListenKeyManager` (interface + REST impl, keepalive) | M1-01, M5-01 | 0008 | FR-UDS-01, FR-UDS-03 | M | keepalive < 30 min; injectable; drop → reconcile fetch |
| WBS-M6-02 | User-data event decode → local order state | M6-01, M4-01 | 0002 | FR-UDS-02 | M | `executionReport` updates the tracked order |

## M7 — Hardening & release (`1.0.0`)

| ID | Title | Deps | ADRs | FRs | Sz | Exit criteria |
|----|-------|------|------|-----|----|---------------|
| WBS-M7-01 | Packaging finalize (semver, wheel, classifiers) | M1–M6 | 0010 | FR-GEN-04 | S | `uv build` wheel imports as `binance_th` |
| WBS-M7-02 | Security toolchain (`bandit`, `pip-audit`, `security.yml`) | — | 0017 | FR-AUTH-03 | M | weekly scan job green; redaction test in CI |
| WBS-M7-03 | `docker-publish.yml` + `LICENSE` + docs polish | M7-01 | 0010 | — | S | tag `v*` → ghcr image; MIT `LICENSE` present |

**Critical path:** `M0 → M1 → M2 → M3 → M4 → M6 → M7` (see [ROADMAP.md](./ROADMAP.md)). The WS branch
`M1 → M3 → M5 → M6` runs in parallel and rejoins at M6.

## Plan gaps found (ambiguities closed)

Ambiguities in the source material (the prompt + `CLAUDE.md` + docstrings — there was **no**
pre-existing build-plan doc) that this suite resolved:

1. **WS host/topology conflict** — config's two hosts (`gstream`/`nstream`) vs the docs' single
   `?streams=` host → **[ADR-0014](./adr/ADR-0014-stream-routing-and-base-url-topology.md)**: routing is
   config data behind a resolver; default to single-host, verify at M5 (WBS-M5-02).
2. **WSA vs `/api/v1/listenKey`** — the `/w3w/wsa/` path hints at a WSA-native auth →
   **[ADR-0008](./adr/ADR-0008-listenkey-lifecycle-and-manager.md)**: REST listenKey behind an
   injectable manager so WSA slots in.
3. **5xx reconciliation mechanics** — "verify before retry" lacked a mechanism →
   **[ADR-0006](./adr/ADR-0006-error-taxonomy-and-5xx-unknown-reconciliation.md)** +
   **[ADR-0013](./adr/ADR-0013-idempotency-and-client-order-id.md)**: pre-minted client id + query-by-id.
4. **Retry/backoff schedule** — `max_retries` existed with no schedule/eligibility →
   **[ADR-0012](./adr/ADR-0012-retry-and-backoff-taxonomy.md)**.
5. **Bare vs wrapped endpoints** — not enumerated → per-endpoint `envelope: bool`
   (**[ADR-0002](./adr/ADR-0002-response-envelope-unwrap.md)**), classified during M3.
6. **Rate-limit unit (weight vs raw)** — ambiguous → seed both windows from `exchangeInfo.rateLimits`
   (**[ADR-0005](./adr/ADR-0005-dual-window-rate-limiter.md)**), don't hardcode.
7. **`accountV2` vs `account`** — standardize on `/api/v1/accountV2`; verify no legacy `/account` path
   at M3.
8. **GLOBAL/SITE parity unknown** — assume none; surface `type`; per-type checks
   (**[ADR-0011](./adr/ADR-0011-global-vs-site-symbol-handling.md)**).
9. **`recvWindow` for `-1021`** — keep `le=60000`, default 5000; offset is primary, `recvWindow` a
   tuning knob (**[ADR-0004](./adr/ADR-0004-server-time-offset-and-1021-resync.md)**).
10. **`SymbolInfo` model mismatch (found in M1 live probe, 2026-07-09)** — the Phase-1 `SymbolInfo`
    (`binance_th/models/base.py`) marks `icebergAllowed`, `ocoAllowed`, `isSpotTradingAllowed`,
    `isMarginTradingAllowed`, and `permissions` as **required**, but the live TH `exchangeInfo` does
    **not** return them (it returns `test`, `baseCommissionPrecision`, `quoteCommissionPrecision`,
    `type`, `filters`, `orderTypes`); the observed filter set is `PRICE_FILTER`, `PERCENT_PRICE`,
    `LOT_SIZE`, `MIN_NOTIONAL`, `MAX_NUM_ORDERS` (no `MARKET_LOT_SIZE`/`PRICE_RANGE`). So
    `ExchangeInfo(**live_response)` would fail. **✓ Fixed in M3a:** `SymbolInfo` reconciled
    (the five global-only fields → `Optional`; `test`/`type`/`baseCommissionPrecision`/
    `quoteCommissionPrecision` added), so `ExchangeInfo(**live)` now parses; `client.exchange_info()`
    caches it and reseeds the rate limiter.
11. **M3 split into M3a + M3b.** **✓ M3a (merged):** public `client.market.*` + `exchange_info`
    (WBS-M3-01/03/04). **✓ M3b:** signed `client.account.*`/`client.wallet.*` **reads** (accountV2,
    userTrades + pagination, tradeFee, deposit address/history + pagination, withdraw history) +
    the signed→bare transport flip (WBS-M3-02, part of M3-03). **Deferred:** wallet **writes**
    (`withdraw`, `sub_account_transfer` — money-movers) to a later gated milestone. **⚠ ASSUMED:** all
    signed shapes are mock-tested only (no credentials) — reconcile in a live soak.
12. **M4 orders (mock-only).** ✓ `client.orders`: create/cancel/query/openOrders with pre-trade
    tick/step **floor-division** snapping + filter validation (ADR-0009), URL-safe client-order-id
    minting (ADR-0013), and 5xx-UNKNOWN reconciliation (query-by-client-id, **never resubmit** —
    ADR-0006, raising `BinanceThOrderUnknownError`). Order placement is signed, real-money, and
    unverifiable → mock-tested only, ⚠ ASSUMED; **no live order test ships**. Deferred/dormant:
    cancel-UNKNOWN reconciliation and active PRICE_RANGE validation.

## Deferred tooling (recorded, intentionally not done in M0)

These are **not** part of the planning PR; they are tracked here so they are not forgotten:

- Add `httpx` (M1) / `websockets` (M5) runtime deps — WBS-M1-02, WBS-M5-01.
- Add `bandit` + `pip-audit` dev deps and `security.yml` (weekly) — WBS-M7-02.
- Add `docker-publish.yml` and an MIT `LICENSE` file — WBS-M7-03.
- **Keep** coverage `--cov-fail-under=90` and the broad ruff set as supersets of the template
  (**[ADR-0010](./adr/ADR-0010-packaging-and-distribution.md)**) — do **not** downgrade.
- Optional migration `[project.optional-dependencies]` → `[dependency-groups]` — orthogonal; not
  scheduled.
