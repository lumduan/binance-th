# ADR-0010 — Packaging and distribution

- **Status:** Accepted
- **Date:** 2026-07-09
- **Governs:** FR-GEN-04 · WBS-M0-01, WBS-M7-01

## Context

The library ships publicly on PyPI. Phase-1 already fixes several packaging facts:
distribution/import names split as **`binance-th`** (PyPI) vs **`binance_th`** (import), Python
`>=3.12`, and a `hatchling` build backend (`pyproject.toml:1-44`). The convention repos (`opendys`,
`python-template`) are uv-native and bilingual. Two intentional divergences from `python-template`
must be recorded so a future contributor does not "helpfully" revert them, and the user has chosen a
**single bilingual README** over the two-file toggle.

## Decision

**We will distribute `binance-th` (import `binance_th`) as a uv-native, hatchling-built,
semver-versioned package with a single bilingual `README.md`.** Versions track the milestone map
([ROADMAP.md](../ROADMAP.md)): `0.1.0` planning/alpha → `0.2.0`–`0.7.0` feature milestones →
`1.0.0` stable. We **keep coverage ≥ 90 %** and the **broader ruff rule set**
(`E,W,F,I,B,C4,UP,ARG,SIM,TCH,PTH,RUF,ASYNC`) as deliberate **supersets** of the template's ≥ 80 %
and `E,F,I,UP,B,SIM`. Runtime deps land with their layers — `httpx` at M1, `websockets` at M5
([ADR-0001](./ADR-0001-async-core-stack.md)) — and the security toolchain (`bandit`, `pip-audit`,
`security.yml`, `docker-publish.yml`) at hardening (M7).

Falsifiable: `uv build` produces a wheel that `import binance_th` loads; `pyproject` keeps
`--cov-fail-under=90` and the broad ruff set; the published name resolves as `pip install binance-th`.

## Consequences

**Positive**

- Clear, reproducible builds (`pyproject` + `uv.lock` as the single source of truth).
- Deps are introduced only when used, keeping earlier milestones installable and lean.
- The superset lint/coverage posture is documented, so it is not silently downgraded to match the
  template.

**Negative / trade-offs accepted**

- Diverging from `python-template` (coverage, ruff set, single README, `[project.optional-dependencies]`
  vs `[dependency-groups]`) means this repo is not a byte-for-byte mirror. Accepted and recorded here.
- A single bilingual README grows long; mitigated by an in-page language switch and a short TOC.

## Alternatives Considered

- **Downgrade to the template's 80 % / narrower ruff set** — rejected: reduces rigor on a
  security-sensitive trading library for cosmetic parity.
- **Two-file `README.md` + `README.th.md` (opendys style)** — rejected by user preference in favor of
  one bilingual file; the trade-off (one long file vs two synced files) was accepted deliberately.
- **PEP 621 `[dependency-groups]` migration now** — deferred to a WBS item; it is orthogonal to the
  planning suite and touches tooling this task intentionally leaves alone.
