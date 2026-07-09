# ADR-0009 — Local pre-trade validation against symbol filters

- **Status:** Accepted
- **Date:** 2026-07-09
- **Governs:** FR-ORD-01, FR-MKT-03 · WBS-M4-03

## Context

An order that violates a symbol's trading filters is rejected server-side, costing a round-trip, a
slice of the rate budget ([ADR-0005](./ADR-0005-dual-window-rate-limiter.md)), and — on a transient
failure — a possible UNKNOWN state ([ADR-0006](./ADR-0006-error-taxonomy-and-5xx-unknown-reconciliation.md)).
`exchangeInfo` publishes the rules per symbol: `PRICE_FILTER` (`tickSize`), `LOT_SIZE` /
`MARKET_LOT_SIZE` (`stepSize`, `minQty`/`maxQty`), and `MIN_NOTIONAL`. ⚠ ASSUMED (verify at
implementation): Binance **Thailand** adds an `executionRules` endpoint exposing a **`PRICE_RANGE`**
band relative to a `referencePrice`. Phase-1 already models these — `SymbolFilter` with all filter
fields, `SymbolInfo.get_filter()`, and `FilterType` including `PRICE_FILTER`/`LOT_SIZE`/`MIN_NOTIONAL`/
`MARKET_LOT_SIZE` (`binance_th/models/base.py:88-233`, `enums.py:137-153`) — and `OrderRequest`
already validates **type-shape** rules (`orders.py` `@model_validator`), but nothing checks the
exchange filters.

## Decision

**We will validate every order locally before it is sent**, against `PRICE_FILTER`, `LOT_SIZE`,
`MARKET_LOT_SIZE`, `MIN_NOTIONAL`, and the TH `executionRules` `PRICE_RANGE`, using a cached
`exchangeInfo`. Prices are snapped to `tickSize` and quantities to `stepSize` with **`ROUND_DOWN`**
(never round up into a more aggressive order); an order that still violates min-notional, lot bounds,
or the price range raises a typed `BinanceThValidationError` **before any network call**.

Falsifiable: a price of `tickSize × 3.7` is floored to `× 3`; an order below `MIN_NOTIONAL` raises
locally with no HTTP request issued; a price outside `PRICE_RANGE` is rejected client-side.

## Consequences

**Positive**

- Turns a class of server rejections into instant, typed, offline errors; saves rate budget and
  latency; removes a source of UNKNOWN mutating-call failures.
- `ROUND_DOWN` is conservative — snapping never makes an order larger or more aggressive than asked.

**Negative / trade-offs accepted**

- Correctness depends on a **fresh** `exchangeInfo`/`executionRules` cache; a stale cache can pass an
  order the server later rejects (still safe, just not saved). Cache TTL + refresh is a WBS concern.
- Duplicates the server's validation locally — the exchange remains the final authority; local checks
  are an optimization, not a substitute.

## Alternatives Considered

- **Let the server validate** — rejected: wastes round-trips and rate budget and forfeits the offline,
  typed failure that makes client code simple.
- **`ROUND_HALF_UP` / nearest tick** — rejected: rounding up can breach a max or make a buy more
  aggressive than intended; `ROUND_DOWN` is the safe default.
