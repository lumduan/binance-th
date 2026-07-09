# Project Skill — Operating Rules

Top-level rules every agent and contributor must follow when working in `binance-th`. These distill
the Architecture Decision Records ([`docs/plans/adr/`](../../docs/plans/adr/README.md)); when a rule
and an ADR disagree, the ADR wins — fix this file.

## Hard Rules

1. **Always `uv run`.** Never call `python`/`pip`/`poetry` directly. `uv sync --extra dev` to install;
   `uv run pytest` / `ruff` / `mypy` to check.
2. **Async-only.** All HTTP goes through one `httpx.AsyncClient`; all WebSockets through `websockets`.
   No synchronous client, no `requests` in library code. (ADR-0001, ADR-0015)
3. **`Decimal` on all money.** Never `float` for any price, quantity, balance, fee, or notional.
   (ADR-0001)
4. **Unwrap the envelope in exactly one place.** `code == 0` → return `data`; `code != 0` → typed
   exception. Bare market-data payloads bypass with `envelope=False`. Don't scatter the check.
   (ADR-0002, ADR-0006)
5. **Sign before send; never log secrets.** Build signed params in insertion order; HMAC-SHA256 over
   the raw concatenation; append `signature` last and never sign it. Never log `api_secret`,
   `signature`, or `listenKey` — redact them. (ADR-0003, ADR-0017)
6. **Validate before ordering.** Snap price→`tickSize` and qty→`stepSize` with `ROUND_DOWN`; check
   `MIN_NOTIONAL`, lot bounds, and TH `PRICE_RANGE` locally before any network call. (ADR-0009)
7. **Never blind-retry a mutating call.** A 5xx/timeout on order create/cancel is *UNKNOWN* — reconcile
   by the minted `newClientOrderId`, don't resubmit. Only non-mutating calls retry (jittered backoff).
   (ADR-0006, ADR-0012, ADR-0013)
8. **GLOBAL vs SITE is never coalesced.** Always surface the symbol `type`; branch where semantics
   differ; base-URL/stream routing is config data behind a resolver, not hardcoded. (ADR-0011, ADR-0014)
9. **Pydantic at the boundary.** Responses subclass `ResponseModel` (`extra="allow"`), requests
   `RequestModel` (`extra="forbid"`); never pass raw dicts between layers. (`binance_th/models/base.py`)
10. **Green before commit.** ≥ 90 % coverage, `ruff check` + `mypy --strict` clean; Conventional
    Commits (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`).

## Soft Conventions

- snake_case Python attributes ↔ camelCase wire keys via `Field(alias="...")`; models accept either.
- Array-shaped endpoints (klines, depth) use `from_list`/`from_api` classmethods — not dict construction.
- New public symbols go into the module `__all__` **and** are re-exported (root `__init__` if top-level).
- Rate-limit windows are **seeded from `exchangeInfo.rateLimits`** and reconciled to `X-MBX-USED-WEIGHT-*`
  headers — never hardcoded. (ADR-0005)
- Each endpoint docstring records path, weight, auth class, and links its `FR-*` + `ADR-*`, with a
  runnable `async` snippet (see the DoD in [`frd.md`](../../docs/plans/frd.md)).
- Binance TH API facts not yet verified against the live docs are marked `⚠ ASSUMED` and confirmed at
  the owning milestone.

## Where to Look First

- [`docs/plans/hld.md`](../../docs/plans/hld.md) — architecture & TH invariants
- [`docs/plans/adr/README.md`](../../docs/plans/adr/README.md) — the 17 decisions
- [`docs/plans/frd.md`](../../docs/plans/frd.md) · [`docs/plans/ROADMAP.md`](../../docs/plans/ROADMAP.md)
- [`CLAUDE.md`](../../CLAUDE.md) — repo architecture, commands, and the single-test coverage gotcha
- `binance_th/models/base.py`, `binance_th/exceptions.py`, `binance_th/config.py` — the Phase-1 seams
