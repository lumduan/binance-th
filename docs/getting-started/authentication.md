# Authentication

[Home](../index.md) > Getting Started > Authentication

**English** · [ไทย](../th/getting-started/authentication.md)

Public market data and market streams need no credentials. Signed reads (account, wallet), order
management, and the user-data stream do. binance-th signs requests for you — you just supply the keys.

## Three access levels

| Level | Needs | Used by |
|-------|-------|---------|
| Public | nothing | `client.market.*`, `client.ws.*`, `ping`, `server_time`, `exchange_info` |
| API-key only | `api_key` | `client.user_stream.*` (listenKey — no HMAC secret) |
| Signed (HMAC) | `api_key` + `api_secret` | `client.account.*`, `client.wallet.*`, `client.orders.*` |

## Supply credentials

The recommended way is a `.env` file (or environment variables) read automatically by
`BinanceThConfig`. The prefix is **`BINANCE_TH_`**:

```bash
# .env  (keep this out of version control)
BINANCE_TH_API_KEY=your_api_key
BINANCE_TH_API_SECRET=your_api_secret
```

```python
from binance_th import BinanceThClient

async with BinanceThClient() as client:      # reads .env / env vars
    info = await client.account.account()
```

Or pass them explicitly:

```python
from binance_th import BinanceThClient, BinanceThConfig

config = BinanceThConfig(api_key="…", api_secret="…")
async with BinanceThClient(config) as client:
    ...
```

`api_secret` is stored as a Pydantic `SecretStr`, so it won't print in reprs or tracebacks. Check what
you have with `config.has_credentials()`.

## Secrets are never logged

Even with `log_requests=True` / `log_responses=True`, the signature, `api_secret`, and any `listenKey`
are redacted before anything reaches a logger (recursively, including nested response bodies). Still,
never commit a real `.env` — a `.env.example` with the correct variable names is provided.

## Signing, handled for you

For signed endpoints the client adds `timestamp` + `recvWindow`, computes the HMAC-SHA256 `signature`,
and tracks the server-time offset (auto-resyncing on a `-1021` "timestamp outside recvWindow" error).
You don't build any of that by hand.

## See Also

- [Errors & reconciliation](../concepts/errors-and-reconciliation.md) — `BinanceThAuthError` and friends
- [Orders guide](../guides/orders.md)
- [User-data stream guide](../guides/user-data-stream.md)
