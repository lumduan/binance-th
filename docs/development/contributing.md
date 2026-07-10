# Contributing

[Home](../index.md) > Development > Contributing

**English** · [ไทย](../th/development/contributing.md)

The full guide lives in [`CONTRIBUTING.md`](../../CONTRIBUTING.md); this page is the short version for
working in the code. Security policy is in [`SECURITY.md`](../../SECURITY.md).

## Setup

This project uses [`uv`](https://docs.astral.sh/uv/) (not pip/poetry) and needs Python **3.12+** (CI also
runs 3.13).

```bash
uv sync --extra dev        # runtime + dev dependencies
```

## The quality gate

CI runs three independent jobs — **lint**, **type-check**, **test** — and all must pass. Run them locally
before pushing:

```bash
uv run ruff format .        # format  (check-only: ruff format --check .)
uv run ruff check . --fix   # lint + autofix
uv run mypy binance_th      # strict type-check
uv run pytest               # tests, ≥90% coverage enforced
uv run pre-commit run --all-files   # everything, incl. hygiene hooks
```

`mypy` is `strict = true`; `ruff` line length is 100 with a broad ruleset (including `ASYNC`).

## Conventions that are easy to miss

- **`Decimal` for money** — never `float`. See [Money & Decimals](../concepts/money-and-decimals.md).
- **Pick the right base model** — responses subclass `ResponseModel` (`extra="allow"`), requests
  subclass `RequestModel` (`extra="forbid"`). See [models](../reference/models.md).
- **Array-format endpoints** get a `from_list`/`from_api` classmethod.
- **Public symbols** go in the module's `__all__` and are re-exported from the package root.
- **GLOBAL vs SITE** is a real split — preserve it in stream/symbol code
  ([concept](../concepts/global-vs-site.md)).

## Commits

Conventional Commits with a phase/scope, e.g. `feat(phase-01): …`, `fix(ci): …`, `docs: …`.

## See Also

- [Testing](testing.md) · [Release process](release-process.md)
- [Architecture overview](../architecture/overview.md)
