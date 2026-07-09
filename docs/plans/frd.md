# Functional Requirements — `binance-th`

Testable requirements, grouped by area, with an `FR-<AREA>-NN` id, a one-line description, at least
one acceptance criterion, a MoSCoW priority, and the governing ADR(s). The area segment keeps ids
greppable across the nine areas and maps cleanly to [adr/](./adr/README.md) and [wbs.md](./wbs.md).
Priorities: **M**ust / **S**hould / **C**ould / **W**on't-yet.

> Every FR is also subject to the global per-endpoint **[Definition of Done](#definition-of-done)** at
> the bottom of this document.

## General

| FR | Description | Acceptance criterion | Prio | ADRs |
|----|-------------|----------------------|------|------|
| FR-GEN-01 | Client construction & async lifecycle | `async with BinanceThClient(cfg) as c:` opens and deterministically closes httpx + WS; no "unclosed connector" warning | M | 0001, 0015 |
| FR-GEN-02 | `exchangeInfo` cache + symbol/filter lookup | `c.exchange_info().get_symbol("BTCTHB")` returns a `SymbolInfo` with its filters, served from cache after first fetch | M | 0009 |
| FR-GEN-03 | Server-time bootstrap & offset | `c.server_time()` populates the signer offset within ±tolerance of the server clock | M | 0004 |
| FR-GEN-04 | Packaging & import identity | `pip install binance-th` then `import binance_th` works; `uv build` yields a wheel | S | 0010 |

## Market Data

| FR | Description | Acceptance criterion | Prio | ADRs |
|----|-------------|----------------------|------|------|
| FR-MKT-01 | Order-book depth | `c.depth(symbol, limit)` returns an `OrderBook` (bare payload) with `Decimal` bids/asks; unknown fields tolerated | M | 0002, 0001 |
| FR-MKT-02 | Klines (paged) | a 3-day 1-minute request returns contiguous, de-duplicated candles across pages | S | 0016, 0002 |
| FR-MKT-03 | TH `referencePrice` / `executionRules` | the `PRICE_RANGE` band for a symbol is retrievable for pre-trade checks | M | 0009, 0011 |

## Account

| FR | Description | Acceptance criterion | Prio | ADRs |
|----|-------------|----------------------|------|------|
| FR-ACC-01 | `accountV2` balances (signed) | a signed `c.account()` succeeds and `get_balance("THB")` returns free/locked `Decimal`s | M | 0003, 0002 |
| FR-ACC-02 | `userTrades` history (paged) | trades are de-duplicated by id across time-window pages | S | 0016 |
| FR-ACC-03 | Trade fee | `c.trade_fee(symbol)` returns maker/taker `Decimal`s | C | 0002 |

## Orders

| FR | Description | Acceptance criterion | Prio | ADRs |
|----|-------------|----------------------|------|------|
| FR-ORD-01 | Place order (validated, idempotent) | a sub-tick price is floored (ROUND_DOWN) or rejected **before** send; the response `Order` echoes the (minted) client id | M | 0009, 0013, 0003 |
| FR-ORD-02 | 5xx UNKNOWN reconciliation | a simulated 503 on POST `/order` triggers a query-by-client-id and produces **no** duplicate order | M | 0006, 0013 |
| FR-ORD-03 | Cancel / query by id-or-clientId | neither `orderId` nor `origClientOrderId` supplied → local `ValueError` before any network call | M | 0006, 0002 |

## Wallet / Fiat

| FR | Description | Acceptance criterion | Prio | ADRs |
|----|-------------|----------------------|------|------|
| FR-WAL-01 | Deposit address / history | `DepositRecord.status` maps to the `DepositStatus` enum | S | 0002 |
| FR-WAL-02 | Withdraw + history (paged) | signed POST returns `WithdrawResult.id`; history is paged; `status` → `WithdrawStatus` | S | 0003, 0016 |
| FR-WAL-03 | Sub-account transfer | `SubAccountTransfer.tx_id` is returned on success | C | 0003 |

## WS Streams

| FR | Description | Acceptance criterion | Prio | ADRs |
|----|-------------|----------------------|------|------|
| FR-WSS-01 | Combined market-stream multiplex | subscribing two symbols yields both streams on one connection; dynamic (un)subscribe works | M | 0014, 0015 |
| FR-WSS-02 | Local order-book maintenance | an injected update-id gap triggers a snapshot re-fetch (no silent divergence) | M | 0007 |
| FR-WSS-03 | GLOBAL vs SITE routing | a SITE symbol subscribes on the SITE route, a GLOBAL symbol on the GLOBAL route | M | 0014, 0011 |

## User-Data Stream

| FR | Description | Acceptance criterion | Prio | ADRs |
|----|-------------|----------------------|------|------|
| FR-UDS-01 | listenKey lifecycle | keepalive is scheduled < 30 min; the key is `DELETE`d on shutdown | M | 0008, 0015 |
| FR-UDS-02 | Event decode | an `executionReport` event updates local order state via a typed model | M | 0002 |
| FR-UDS-03 | Drop reconciliation | after a reconnect, local order state equals the REST `openOrders` + `userTrades` truth | S | 0008 |

## Rate Limiting

| FR | Description | Acceptance criterion | Prio | ADRs |
|----|-------------|----------------------|------|------|
| FR-RL-01 | Dual-window pacing | exceeding ~1000 weight/10 s **delays** the next call rather than 429-ing | M | 0005 |
| FR-RL-02 | Header reconciliation | a server `X-MBX-USED-WEIGHT-*` above the local counter raises the local counter to match | M | 0005 |
| FR-RL-03 | Order-count limiter + hard-stop | a 429/418 honors `Retry-After` and halts the affected class | M | 0005, 0012 |

## Auth / Signing

| FR | Description | Acceptance criterion | Prio | ADRs |
|----|-------------|----------------------|------|------|
| FR-AUTH-01 | HMAC signing & param order | a golden vector (known params + secret) reproduces a known signature; reordering params changes it | M | 0003 |
| FR-AUTH-02 | `timestamp` + `recvWindow` + `-1021` | a simulated single `-1021` resyncs and retries exactly once | M | 0004 |
| FR-AUTH-03 | Secret redaction | with `log_requests=True`, captured logs contain **no** signature/secret/listenKey value | M | 0017 |

## Definition of Done

A single per-endpoint rubric; an endpoint is not "done" until all hold:

- **Typed in/out** — typed params or a `RequestModel` (extra=forbid); response into a `ResponseModel`
  (extra=allow) or a documented bare-array parser (`from_list`/`from_api`).
- **Auth class declared & enforced** — PUBLIC / API-KEY-only / SIGNED, and signed if required (ADR-0003).
- **Envelope handling declared** — wrapped vs bare per endpoint (ADR-0002).
- **Weight registered** — the call charges the rate limiter; order endpoints also charge the order
  counter (ADR-0005).
- **Errors mapped** — routed through the taxonomy; mutating endpoints implement UNKNOWN reconciliation
  (ADR-0006, 0013).
- **Money is `Decimal`**, and every alias matches the exact wire key.
- **Tests** — ≥ 1 mocked unit test covering happy path + one validation failure + one envelope/HTTP
  error, using `httpx.MockTransport`; repo coverage stays ≥ 90 %.
- **Docstring** — records path, weight, auth class, and links its FR-ID + ADR(s), with a runnable
  `async` snippet.
- **Public surface** — new symbols added to the module `__all__` and re-exported (root `__init__` if
  top-level).
- **No secret leakage** (ADR-0017); `ruff` + `mypy --strict` clean.
