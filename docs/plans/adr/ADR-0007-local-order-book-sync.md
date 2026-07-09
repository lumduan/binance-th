# ADR-0007 — Local order-book (depth) synchronization

- **Status:** Accepted
- **Date:** 2026-07-09
- **Governs:** FR-WSS-02 · WBS-M5-03

## Context

A live local order book is built by combining a REST depth **snapshot** with a WebSocket stream of
depth **deltas**. Applied naively, the two race: deltas arrive before the snapshot is fetched, or a
dropped WS message leaves the book silently diverged from the exchange — a dangerous state for a
trading client. The canonical Binance procedure uses each event's update-id range (`U`..`u`) to
splice the streams together and to detect gaps. Phase-1 has the data model (`OrderBook`,
`OrderBookEntry` with `Decimal` levels, `binance_th/models/market.py:15-61`) but no maintenance
engine, and must also choose a container for price levels.

## Decision

**We will synchronize the book with the buffer→snapshot→drop→apply→gap-resync algorithm:** (1) open
the depth stream and **buffer** deltas; (2) fetch the REST depth snapshot with its `lastUpdateId`;
(3) **drop** buffered deltas fully older than the snapshot (`u <= lastUpdateId`); (4) verify the first
applied delta **brackets** the snapshot (`U <= lastUpdateId+1 <= u`), else re-snapshot; (5) **apply**
deltas in order, updating/removing levels (quantity `0` removes a level); (6) on **any update-id gap**
(`U > last_applied_u + 1`) discard the book and **re-snapshot**. Price levels are held in a plain
`dict[Decimal, Decimal]` (O(1) upsert/remove) with **on-demand sorting** for top-N reads — zero new
dependency for v1.

Falsifiable: an injected update-id gap forces a snapshot re-fetch (not silent divergence); replaying
a recorded delta sequence yields a book identical to the exchange's reference at the same update-id.

## Consequences

**Positive**

- Detects desync deterministically instead of trusting the stream; correctness over cleverness.
- Zero-dependency container keeps the security surface small; top-of-book reads stay cheap.

**Negative / trade-offs accepted**

- Full-depth sorted iteration costs `O(n log n)` per read (dict + sort). Acceptable because most
  consumers want top-N; revisit with `sortedcontainers.SortedDict` only if profiling shows it hot.
- A gap forces a full re-snapshot (a REST call + rebuild) rather than an incremental repair.

## Alternatives Considered

- **`sortedcontainers.SortedDict` from the start** — deferred, not rejected: adds a dependency for a
  benefit (ordered iteration) that top-N reads rarely need; promotable later behind the same interface.
- **Apply deltas without gap detection** — rejected: the whole point is to catch the dropped-message
  divergence that makes a local book unsafe.
- **Trust the WS stream alone (no REST snapshot)** — rejected: deltas are meaningless without the
  absolute baseline the snapshot provides.
