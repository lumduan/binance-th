# ADR-0001 — Async-only core stack (httpx + websockets + Pydantic v2 + Decimal)

- **Status:** Accepted
- **Date:** 2026-07-09
- **Governs:** FR-GEN-01 · WBS-M1-01, WBS-M1-02

## Context

`binance-th` targets programmatic trading, where a caller typically fans out many concurrent REST
calls and holds several long-lived WebSocket streams. That workload is I/O-bound and benefits from
cooperative concurrency rather than threads. The library must pick its core runtime primitives
**once**, up front, because every later layer (transport, signing, rate limiter, resource clients,
WS client) is written against them and a change here is a rewrite.

Phase-1 code already commits to two of these choices: models subclass Pydantic v2
`BaseModel`/`ConfigDict` (`binance_th/models/base.py`) and every monetary field is `Decimal`
(`binance_th/models/{market,account,orders}.py`). What remains open is the HTTP and WebSocket
clients and whether we also ship a synchronous facade.

Constraints: Python `>=3.12` (`pyproject.toml`), MIT-licensed pure-Python deps, and a small
dependency surface for a security-sensitive package.

## Decision

**We will build the library async-only.** All I/O uses `async`/`await`; HTTP goes through a single
`httpx.AsyncClient`, WebSockets through the `websockets` library, request/response bodies are
Pydantic v2 models, and **every price, quantity, balance, fee, and notional is `Decimal`** — never
`float`. We will **not** ship a synchronous client or a sync shim in v1.

Falsifiable: a grep of `binance_th/` finds no `requests`, no `float(` on a money path, and no
public sync client class; `mypy --strict` passes with `httpx`/`websockets` typed at the boundary.

## Consequences

**Positive**

- One code path to test and maintain; true concurrency for REST fan-out and multiplexed streams.
- `httpx.AsyncClient` gives connection pooling, HTTP/2, and a first-class `MockTransport` for
  deterministic unit tests without a network (supports the DoD's "mocked transport" rule).
- `Decimal` end-to-end eliminates binary-float rounding on order prices/quantities.

**Negative / trade-offs accepted**

- Callers must run inside an event loop; users wanting blocking calls must wrap with
  `asyncio.run(...)` themselves. Accepted — the target audience is async.
- Two runtime network dependencies (`httpx`, `websockets`) beyond `pydantic`. Added at M1/M5 (see
  [ADR-0010](./ADR-0010-packaging-and-distribution.md)), not now.

## Alternatives Considered

- **`aiohttp`** — rejected: `httpx` has a cleaner API, sync+async parity for docs examples, HTTP/2,
  and a superior test-transport story.
- **`requests` + a sync core with an async wrapper** — rejected: blocks the loop, forces threads for
  concurrency, and doubles the surface area.
- **`float` for money with `Decimal` only at the edge** — rejected: intermediate float arithmetic
  reintroduces the rounding we are trying to avoid; tick/step snapping (ADR-0009) needs exact math.
