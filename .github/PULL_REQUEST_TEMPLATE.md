## What & why

<!-- What does this change and why? Link any issue or ADR. -->

## Checklist

- [ ] `uv run pytest` green (≥90% coverage)
- [ ] `uv run ruff format --check .` + `uv run ruff check .` clean
- [ ] `uv run mypy binance_th` clean (strict)
- [ ] Conventional Commit title (e.g. `feat(...)`, `fix(...)`, `docs: ...`)
- [ ] New public symbols added to `__all__` and re-exported (if any)
- [ ] No secret in logs/tests; redaction extended if a new credential field was added (ADR-0017)
- [ ] `Decimal` for money; correct `ResponseModel`/`RequestModel` base + aliases
