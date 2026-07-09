# ADR-0002 — Centralized response-envelope unwrapping

- **Status:** Accepted
- **Date:** 2026-07-09
- **Governs:** FR-MKT-01, FR-ACC-01, FR-UDS-02 · WBS-M1-03

## Context

Binance Thailand returns most REST responses inside an envelope
`{"code": 0, "msg": "", "timestamp": <ms>, "data": <payload>}`, where **`code == 0` means success**
and any other `code` is a failure carrying `msg`. This is documented in the Phase-1 exception
module docstring (`binance_th/exceptions.py:26-32`). ✓ VERIFIED (2026-07-09, live probe): public
market/system endpoints return **bare** payloads — `GET /api/v1/time` → `{"serverTime":…}`,
`GET /api/v1/exchangeInfo` → a bare object, and `GET /api/v1/ping` → the non-JSON literal `pong` —
all under `/api/v1/`. The `{code,msg,timestamp,data}` envelope is therefore a **signed-endpoint**
convention (not observable on public endpoints without credentials), matching the array parsers
already written (`OrderBook.from_api`, `Kline.from_list` in `binance_th/models/market.py`). The
implemented default is **bare for unsigned, enveloped for signed**.

If each resource client unwrapped the envelope itself, the `code == 0` check and error mapping would
be duplicated across dozens of endpoints and drift. We need exactly one seam that turns a raw HTTP
response into a validated payload, while still allowing the bare-payload endpoints through.

## Decision

**We will unwrap the envelope in one place in the transport layer.** A single helper inspects the
decoded JSON: if it is an envelope, it asserts `code == 0` and returns `data`, routing a non-zero
`code` to the typed-exception mapper ([ADR-0006](./ADR-0006-error-taxonomy-and-5xx-unknown-reconciliation.md));
callers that hit bare-payload endpoints pass `envelope=False` to bypass the unwrap and receive the
raw JSON for a `from_list`/`from_api` parser. All response models keep `extra="allow"`
(`ResponseModel`, `binance_th/models/base.py:25`) so new server fields never break decoding.

Falsifiable: a `code != 0` envelope raises the mapped exception (never returns data); a bare `depth`
dict parses via `OrderBook.from_api` without a `data` key; both paths have unit tests.

## Consequences

**Positive**

- The `code == 0` contract and error routing live once; every endpoint inherits them.
- Forward-compatible: `extra="allow"` + centralized unwrap absorb API drift without code changes.

**Negative / trade-offs accepted**

- Every endpoint must be **classified** wrapped-vs-bare (a per-endpoint `envelope: bool`), and a
  wrong classification surfaces as a decode/parse error. Mitigated by the per-endpoint DoD checkbox
  and a test per endpoint; the true bare/wrapped set is confirmed during M3 implementation.

## Alternatives Considered

- **Unwrap inside each Pydantic model** (a validator that reaches for `data`) — rejected: scatters
  the `code` check, can't uniformly raise typed errors, and breaks bare payloads.
- **Assume every response is wrapped** — rejected: bare market-data payloads have no `data` key and
  would fail to parse.
- **Assume every response is bare and let models pick fields** — rejected: loses the `code`/`msg`
  failure signal that distinguishes an application error from an HTTP error.
