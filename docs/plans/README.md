# binance-th — Planning & Engineering Docs

This folder is the **canonical blueprint** for `binance-th`: the source of truth for intent,
decisions, and roadmap. Code implements what is decided here. Layout and conventions mirror
[`lumduan/opendys`](https://github.com/lumduan/opendys)'s `docs/plans/`.

## Document types

| Type | File(s) | Purpose |
| --- | --- | --- |
| **ROADMAP** | [`ROADMAP.md`](./ROADMAP.md) | Master phased plan (M0–M7 → semver) and status index. |
| **HLD** | [`hld.md`](./hld.md) | High-Level Design: architecture, layers, TH invariants, non-goals. |
| **FRD** | [`frd.md`](./frd.md) | Functional Requirements: `FR-<AREA>-NN` table + Definition of Done. |
| **WBS** | [`wbs.md`](./wbs.md) | Work Breakdown Structure: milestones → `WBS-Mn-NN` items + plan gaps. |
| **ADR** | [`adr/`](./adr/README.md) | Architecture Decision Records — one accepted decision each, immutable. |

## Naming conventions

- Files are `kebab-case`; the design-doc trio stays lowercase — `hld.md`, `frd.md`, `wbs.md` — while
  `ROADMAP.md` and `README.md` keep their conventional casing.
- ADRs: `ADR-00NN-short-slug.md`, zero-padded to 4 digits, monotonically increasing, never renumbered.
- IDs are greppable and cross-linked: `ADR-00NN` ⇄ `FR-<AREA>-NN` ⇄ `WBS-Mn-NN`.

## Traceability spine

Every decision is falsifiable and connected to a requirement and a work item:

```
ADR-00NN  ──governs──▶  FR-<AREA>-NN  ──delivered by──▶  WBS-Mn-NN  ──scheduled in──▶  ROADMAP Mn
```

Each ADR's `**Governs:**` line names its FRs and WBS items; each FR row names its ADRs; the WBS and
ROADMAP reference ADR-IDs. To audit coverage, grep an id in all four files.

## Status legend

| Mark | Meaning |
| --- | --- |
| `[ ]` | Not started |
| `[~]` | In progress |
| `[x]` | Complete |
| `[-]` | Skipped / deferred |

## Workflow

```
Decide (ADR)  →  Specify (FR)  →  Break down (WBS)  →  Schedule (ROADMAP)  →  Implement in binance_th/
   →  Update ROADMAP / WBS status
```

- ADRs are **immutable**. To change a decision, write a new ADR and set the old one's status to
  `Superseded by ADR-00XX`.
- Binance TH API claims not yet verified against the live docs are flagged `⚠ ASSUMED (verify at
  implementation)` in the relevant ADR's Context, and re-checked at the owning milestone.

## Local conventions & divergences

- **Single bilingual `README.md`** (English + ไทย in one file) instead of `opendys`'s two-file
  `README.md`/`README.th.md` toggle — a deliberate project choice
  ([ADR-0010](./adr/ADR-0010-packaging-and-distribution.md)).
- A **standalone ADR index** ([`adr/README.md`](./adr/README.md)) is provided (an addition over
  `opendys`, which lists ADRs inline in its ROADMAP).
- Coverage stays **≥ 90 %** and the ruff rule set stays **broad** — supersets of `python-template`'s
  ≥ 80 % / `E,F,I,UP,B,SIM` (ADR-0010).

## Templates

- ADR: [`adr/ADR-0000-template.md`](./adr/ADR-0000-template.md)
