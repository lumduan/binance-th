# Security Policy

## Reporting a vulnerability

Please report security issues **privately** via
[GitHub Security Advisories](https://github.com/lumduan/binance-th/security/advisories/new)
rather than opening a public issue. We aim to acknowledge reports within a few business days and
will coordinate a fix and disclosure timeline with you.

## Supported versions

The latest `1.x` release receives security fixes.

## Secret handling (ADR-0017)

This is a trading library, so credential hygiene is a first-class concern:

- `api_secret` is stored as a `SecretStr`. The HMAC **signature**, **`api_secret`**, and
  **`listenKey`** are **never logged**. When the `log_requests` / `log_responses` debug flags are
  enabled, credential-bearing fields are **redacted recursively** (including nested response
  bodies) before anything reaches a logger.
- Source is scanned with **`bandit`** and dependencies are audited weekly with **`pip-audit`**
  (`.github/workflows/security.yml`).
- **Never commit real credentials.** Use a gitignored `.env` (see `.env.example`); the library
  reads `BINANCE_TH_`-prefixed environment variables.

## Trading risk

Order endpoints move real money. Validate order state before retrying on a `5xx` (the client
treats a `5xx` as *unknown*, not *failed*), and never run the credentialed soak/probe scripts in
`scripts/` without understanding that they place or manage real orders/keys on your account.
