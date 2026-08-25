# Changelog

All notable changes to this project are documented in this file. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **CI security scan (`security.yml`):** resolved two advisories that held the weekly scan
  red for three consecutive runs (2026-08-10 / 08-17 / 08-24) — `cryptography` 49.0.0 →
  50.0.0 (PYSEC-2026-3552, via `twine` → `keyring` → `secretstorage`) and `pip` 26.1.2 →
  26.2.1 (PYSEC-2026-3721, via `pip-audit`'s own `pip-api`). Both are dev-only; neither is
  reachable from an installed `binance-th`.
- **Node 20 runner deprecation:** bumped every GitHub Action off the deprecated Node 20
  runtime — `actions/checkout` v4 → v7, `astral-sh/setup-uv` v4 → v10.0.1 (that action no
  longer publishes moving major tags, so it is pinned to a full version),
  `codecov/codecov-action` v4 → v7 (its `file:` input is now `files:`), and
  `softprops/action-gh-release` v2 → v3.

### Changed

- **Dependency audit is now scoped by blast radius.** `pip-audit` is split into a
  **blocking** job over the runtime-only closure — exactly what `pip install binance-th`
  installs — and an **advisory** (`continue-on-error`) job over the full dev toolchain. A
  CVE in `ruff`/`mypy`/`twine`/`pip-audit` itself no longer blocks merges, while a CVE that
  actually reaches users still fails the build.

### Added

- `.github/dependabot.yml` — weekly grouped updates for GitHub Actions and `uv.lock`.

## [1.0.0] - 2026-07-10

First stable release — a typed, async-first client for the Binance **Thailand** REST + WebSocket API.

### Added

- **Transport & auth (M1):** async `httpx` transport with bare-response handling, HMAC-SHA256
  request signing, server-time offset (`-1021` resync), a typed error taxonomy (with the
  5xx-UNKNOWN reconciliation rule), deterministic session lifecycle, and secret redaction.
- **Rate limiting (M2):** dual-window token bucket reconciled from `x-mbx-used-weight` headers,
  with jittered exponential retry/backoff.
- **REST — market & account (M3):** market data, `account`/wallet reads, cached
  `exchangeInfo`/`executionRules`, and time-window pagination. Namespaced sub-clients
  (`client.market` / `account` / `wallet`).
- **REST — orders (M4):** `client.orders` create/cancel/query/openOrders with local pre-trade
  validation (tick/step snapping, filter bounds), URL-safe client-order-id minting, and
  5xx-UNKNOWN order reconciliation.
- **WebSocket market streams (M5):** `client.ws` — `watch_depth`/`watch_trades`/
  `watch_agg_trades`/`watch_klines`/`watch_book_ticker`/`watch_ticker` async iterators and a
  self-syncing local order book (ADR-0007), over dual-host GLOBAL/SITE routing with supervised
  reconnect. Shapes live-verified.
- **User-data stream (M6):** `client.user_stream` — a dual (GLOBAL/SITE) listenKey manager with
  keepalive, `watch_orders`/`watch_account`/`watch_balances`, and a self-healing, drop-reconciled
  order tracker (ADR-0008). Lifecycle live-verified.
- **Packaging & hardening (M7):** PEP 561 `py.typed`, `1.0.0` release, a weekly `bandit` +
  `pip-audit` security scan, an enforced ≥90% coverage gate, and a PyPI publish workflow.

### Notes

- User-data event *shapes* (`executionReport` / `outboundAccountPosition` / `balanceUpdate`) are
  modelled to the standard Binance shapes and remain to be confirmed by a supervised order-activity
  soak (`scripts/soak_userdata.py`).

[1.0.0]: https://github.com/lumduan/binance-th/releases/tag/v1.0.0
