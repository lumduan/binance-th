# ADR-0017 — Secret redaction and logging policy

- **Status:** Accepted
- **Date:** 2026-07-09
- **Governs:** FR-AUTH-03 · WBS-M1-07, WBS-M7-02

## Context

Config exposes `log_requests` and `log_responses` debug flags (`binance_th/config.py:127-134`). Turned
on with the naive implementation they imply — "log the full request/response" — they would write the
**HMAC `signature`**, and potentially the **`api_secret`** and **`listenKey`**, into logs. That is a
real credential-leak path: a signature plus its params can be replayed within `recvWindow`, a
`listenKey` grants the user-data stream, and the secret is total compromise. The secret is already a
`SecretStr` (`config.py:65`), and `SecretStr` masks in reprs — but string-formatting a request dict
for a log bypasses that protection.

## Decision

**We will never log `api_secret`, `signature`, or `listenKey`.** When `log_requests`/`log_responses`
are enabled, the logging path **redacts** those (and any future credential-bearing) fields to a
`***`-style placeholder **before** emission; `api_secret` stays a mandatory `SecretStr` and is never
stringified into a log record. This policy is the anchor for the M7 security tooling —
`bandit`, `pip-audit`, and a scheduled `security.yml`.

Falsifiable: with `log_requests=True`, captured log output for a signed call contains **no**
`signature`/`secret`/`listenKey` value (only redacted placeholders); a test asserts the redaction on
a representative signed request.

## Consequences

**Positive**

- Debug logging is safe to enable in real environments; no replayable material reaches logs.
- Establishes the security posture that `bandit`/`pip-audit`/`security.yml` enforce at M7.

**Negative / trade-offs accepted**

- Redacted debug logs are slightly less complete (you cannot see the exact signature) — an acceptable,
  intentional loss for a security-sensitive library.
- The redaction list must be maintained as new credential-bearing fields appear (mitigated by a
  central allow/deny list and a test).

## Alternatives Considered

- **Log everything when the debug flag is on** — rejected: leaks replayable credentials; the flag would
  be unusable in practice.
- **Remove the logging flags entirely** — rejected: request/response logging is genuinely useful for
  debugging; redaction keeps the utility without the leak.
- **Rely on `SecretStr` masking alone** — rejected: it protects the secret's `repr`, not a hand-built
  request dict or the derived `signature`.
