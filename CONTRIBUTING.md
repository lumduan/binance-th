# Contributing

Thanks for your interest! This project uses **[uv](https://docs.astral.sh/uv/)** (not pip/poetry)
and targets Python **3.12+**.

## Setup

```bash
uv sync --extra dev
```

## Checks — green before every commit

```bash
uv run pytest                       # full suite; enforces >=90% branch coverage
uv run ruff format .                # auto-format
uv run ruff check . --fix           # lint + autofix
uv run mypy binance_th              # strict type-check
uv run pre-commit run --all-files   # ruff, ruff-format, mypy --strict, hygiene
```

### Running one test — important gotcha

`[tool.pytest.ini_options] addopts` hard-codes `--cov-fail-under=90`, so running a subset makes
coverage look low and pytest exits non-zero **even when the selected tests pass**. Disable
coverage for a focused run:

```bash
uv run pytest tests/test_orders.py::TestOrderRequest::test_valid_limit_order --no-cov
```

## Conventions

- **[Conventional Commits](https://www.conventionalcommits.org/)** with milestone scopes, e.g.
  `feat(m6): ...`, `fix(ci): ...`, `docs: ...`.
- **`Decimal` for all money** — never `float`. Response models subclass `ResponseModel`
  (`extra="allow"`); request models subclass `RequestModel` (`extra="forbid"`).
- snake_case attributes map to camelCase wire keys via `Field(alias=...)`.
- A new public symbol must be added to its module's `__all__` and re-exported.
- Keep coverage **≥90%** and the broad ruff set — do **not** downgrade (ADR-0010).
- Never log secrets; extend `binance_th/redaction.py` if a new credential-bearing field appears
  (ADR-0017).

## Architecture

The design is captured in `docs/plans/` — an HLD, an FRD, a WBS, a ROADMAP, and 17 ADRs. Read the
relevant ADR before changing a load-bearing convention.
