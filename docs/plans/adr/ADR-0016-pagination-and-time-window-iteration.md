# ADR-0016 — Pagination and time-window iteration

- **Status:** Accepted
- **Date:** 2026-07-09
- **Governs:** FR-MKT-02, FR-ACC-02, FR-WAL-02 · WBS-M3-03

## Context

History endpoints — `userTrades`, `klines`, deposit/withdraw history — cap each response at a server
`limit` and are windowed by `startTime`/`endTime`. Fetching a multi-day range therefore requires
iterating windows and stitching pages, and doing it wrong yields **duplicated or skipped** rows at
window boundaries (an off-by-one on an inclusive timestamp re-fetches the boundary row). Without one
contract this logic gets re-implemented per endpoint, inconsistently.

## Decision

**We will expose history as an async generator that iterates half-open `[startTime, endTime)`
windows** under the server `limit`, advancing each window to the last row's timestamp/id and
**de-duplicating by id** across boundaries. The generator yields typed rows lazily so callers can stop
early, and it charges each underlying page to the rate limiter
([ADR-0005](./ADR-0005-dual-window-rate-limiter.md)).

Falsifiable: iterating a 3-day 1-minute kline range yields contiguous, strictly increasing,
**de-duplicated** candles across page boundaries; a `userTrades` range spanning more than one `limit`
page returns each trade id exactly once.

## Consequences

**Positive**

- One correct paging contract shared by every history endpoint; boundaries handled once.
- Lazy iteration bounds memory and lets callers short-circuit large ranges.

**Negative / trade-offs accepted**

- The half-open convention must be applied consistently; an endpoint whose server semantics are
  inclusive needs a documented adapter (⚠ verify each endpoint's boundary semantics at implementation).
- De-dup requires holding the boundary window's ids briefly — negligible memory.

## Alternatives Considered

- **Return a single page and let callers paginate** — rejected: pushes boundary/dedup bugs onto every
  caller.
- **Eagerly collect the full range into a list** — rejected: unbounded memory for large ranges and no
  early-stop.
- **Inclusive `[start, end]` windows** — rejected: re-fetches the boundary row, the classic
  double-count.
