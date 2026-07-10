# ADR-0014 — Stream routing and base-URL topology

- **Status:** Accepted
- **Date:** 2026-07-09
- **Governs:** FR-WSS-01, FR-WSS-03 · WBS-M5-01

## Context

There is a **direct conflict** between the repo and the live docs about WebSocket topology, and it
must be resolved deliberately rather than by trusting one source. Phase-1 config hardcodes **two**
WebSocket hosts, one per symbol type — `ws_base_url_global = wss://www.binance.th/gstream` and
`ws_base_url_site = wss://www.binance.th/nstream` (`binance_th/config.py:75-82`). The live API console,
however, indicates a **single** WebSocket host using a combined-stream query form —
`wss://nbstream.binance.th/w3w/wsa/stream?streams=<a>/<b>/…` (⚠ ASSUMED — two independent doc fetches
agreed, but the JS console was not byte-verified). We cannot let this ambiguity harden into scattered
`if global: … else: …` URL-building.

## Decision

**We will make base-URL and stream routing a single config-driven resolver seam** — the
GLOBAL/SITE→host mapping and the URL form (combined `?streams=` vs per-stream path) are **data**, not
branching logic — and we will **default to the single-host `?streams=` form** the docs indicate while
**retaining the two existing config fields as override knobs**. The physical route a subscription
takes is computed by the resolver from the symbol's `type`
([ADR-0011](./ADR-0011-global-vs-site-symbol-handling.md)); no client code hardcodes a host. The
default is confirmed against the live console during **M5** before cutover.

Falsifiable: switching the host mapping in config re-routes subscriptions with **no** client-code
change; a SITE symbol and a GLOBAL symbol each resolve to their configured route; the combined-stream
URL is built from the resolver, not string-concatenated at call sites.

## Consequences

**Positive**

- The unresolved topology becomes a one-line config change, not a refactor, whichever form is correct.
- Keeps [ADR-0011](./ADR-0011-global-vs-site-symbol-handling.md) (semantics) cleanly separate from
  physical routing.

**Negative / trade-offs accepted**

- We ship a **default that is still ASSUMED**; if the live console proves the two-host form, the
  default flips (config-only) at M5. Documented as a WBS verification gate, not a silent guess.

## Live verification (M5 · WBS-M5-02 · 2026-07-09)

Probed the real feed read-only (`scripts/probe_ws.py`). **The single-host default is FLIPPED to
dual-host** — exactly the reversible outcome this ADR planned for:

- `wss://nbstream.binance.th/w3w/wsa/stream?streams=…` **connects and ACKs SUBSCRIBE**
  (`{"id":…, "result":null}`) **but pushed no market data** in-window — it is the WSA
  request/response host, not a market-stream push host. Kept as the `ws_base_url` field (reserved,
  likely M6/user-data), **not** the market-stream default.
- **Verified working topology = the two config hosts:** GLOBAL symbols stream on
  `wss://www.binance.th/gstream`, SITE symbols on `wss://www.binance.th/nstream`, both delivering the
  combined **`{"stream": …, "data": …}`** envelope. The `StreamRouter` therefore routes by symbol
  `type` to `ws_base_url_global` / `ws_base_url_site` by default (still pure config data — flipping is
  a two-field change, no client-code change, satisfying the falsifiable criterion).
- **Consequence:** GLOBAL and SITE live on **different hosts**, so a client watching both types holds
  **one connection per host** (up to two), keyed by host in `StreamClient` — the `?streams=` combined
  URL is the verified subscription mechanism on each.

## Alternatives Considered

- **Trust config's two hosts** — rejected: contradicts the current docs and would bake a likely-stale
  topology into stream code.
- **Trust the docs' single host and delete the config fields** — rejected: discards a usable override
  and commits to an unverified claim; keeping both as data is reversible.
- **Hardcode either form at call sites** — rejected: turns a data question into a code refactor.
