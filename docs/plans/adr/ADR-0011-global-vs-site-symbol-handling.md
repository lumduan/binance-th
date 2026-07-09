# ADR-0011 — GLOBAL vs SITE symbol-type handling

- **Status:** Accepted
- **Date:** 2026-07-09
- **Governs:** FR-WSS-03, FR-MKT-03 · WBS-M3-04, WBS-M5-02

## Context

Binance Thailand is a regional instance that serves two classes of trading pair: **GLOBAL** symbols
(shared with the wider Binance platform) and **SITE** symbols (specific to the TH instance). The
distinction is a first-class, TH-specific concept already visible across Phase-1: the `SymbolType`
enum (`GLOBAL`/`SITE`, `binance_th/models/enums.py:93-101`), a dedicated `symbolType` endpoint model
(`SymbolTypeInfo`, `base.py:62-70`), the listenKey's `symbol_type` field (`account.py:199`), and —
tellingly — **two different WebSocket base URLs** in config, one per type
(`ws_base_url_global` → `/gstream`, `ws_base_url_site` → `/nstream`; `config.py:75-82`).

✓ VERIFIED (2026-07-09, live `GET /api/v1/exchangeInfo`): every symbol carries a `"type"` field
(e.g. `"type":"GLOBAL"`), so the marker is present to branch on. ⚠ ASSUMED (needs cross-type
comparison): the two types do **not** guarantee behavioral parity — available filters,
`executionRules`, and stream routing may differ. Code that silently treats a symbol as type-agnostic
risks subscribing a SITE symbol on a GLOBAL route or assuming a filter that only GLOBAL symbols carry.

## Decision

**We will surface the symbol `type` on every symbol-scoped model and API, assume no parity between
GLOBAL and SITE, and require callers to branch where semantics differ.** No code path silently
coalesces the two. The *physical* routing that the type implies (which host/stream a subscription
uses) is owned by [ADR-0014](./ADR-0014-stream-routing-and-base-url-topology.md); this ADR governs the
*semantic* rule that type is always explicit and never assumed away.

Falsifiable: a symbol's `type` is reachable wherever the symbol is (never dropped); a SITE symbol
resolves to SITE routing and a GLOBAL symbol to GLOBAL routing (ADR-0014); no function assumes a
filter/rule exists without checking, per type.

## Consequences

**Positive**

- Prevents a whole class of "worked for GLOBAL, broke for SITE" bugs by making type explicit.
- Keeps TH's regional model faithful rather than flattening it to the global API shape.

**Negative / trade-offs accepted**

- Callers occasionally must branch on `type`, which is slightly more verbose than a unified API —
  accepted as the honest cost of a genuinely bifurcated exchange.

## Alternatives Considered

- **Treat all symbols uniformly and infer type internally** — rejected: hides a real behavioral split
  and mis-routes streams.
- **Expose type only on `exchangeInfo`, not on downstream models** — rejected: the information is
  needed at subscription and validation time, far from `exchangeInfo`.
