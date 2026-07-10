# Release process

[Home](../index.md) > Development > Release process

**English** · [ไทย](../th/development/release-process.md)

`binance-th` is on PyPI: <https://pypi.org/project/binance-th/>. The version is **dynamic** — hatchling
reads `binance_th.__version__` from `binance_th/__init__.py`, so there is no `version` in
`pyproject.toml`. Bump the version there.

Two independent things happen at release: **PyPI upload** (a local, token-based script) and a **GitHub
Release** (a tag-triggered workflow). They are decoupled on purpose.

## 1. Publish to PyPI — `scripts/publish.sh`

```bash
./scripts/publish.sh
```

The script:

1. Loads **only** `PYPI_TOKEN` from a gitignored `.env` (a targeted parse — it does not `export` the
   whole file).
2. Reads the package name from `pyproject.toml` and the version from `import binance_th`.
3. `uv build`, then `uv run twine check dist/*`.
4. Validates the token (must start with `pypi-`) and asks for confirmation.
5. `uv run twine upload dist/* --username __token__ --password "$PYPI_TOKEN"`.

> ⚠ Publishing is **public and irreversible** — a version can never be re-uploaded. Bump the version for
> any change. The token must be **account-scoped** (a project-scoped token from another project cannot
> upload a new project — that returns `403`).

## 2. Tag → GitHub Release — `.github/workflows/release.yml`

```bash
git tag v1.0.0 && git push origin v1.0.0
```

Pushing a `v*` tag triggers the **Release** workflow, which runs `uv build`, `twine check`, and cuts a
GitHub Release with the sdist + wheel attached and auto-generated notes. It does **not** publish to PyPI
(so it needs no PyPI secrets or trusted-publisher setup) — that is `publish.sh`'s job.

## Typical order

1. Bump `__version__`, update [`CHANGELOG.md`](../../CHANGELOG.md), merge to `main`.
2. `./scripts/publish.sh` → PyPI.
3. `git tag vX.Y.Z && git push origin vX.Y.Z` → GitHub Release.

## See Also

- [Contributing](contributing.md) · [Testing](testing.md)
- [Packaging ADR](../plans/adr/ADR-0010-packaging-and-distribution.md)
