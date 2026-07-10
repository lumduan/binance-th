# BinanceThConfig Reference

[Home](../index.md) > Reference > config

**Module:** `binance_th.config` · **Available since:** 1.0.0

Settings for the client. A `pydantic-settings` model: every field reads from an environment variable
prefixed `BINANCE_TH_` (case-insensitive) or a `.env` file, and can also be passed directly. Unknown env
vars are ignored.

## Import

```python
from binance_th import BinanceThConfig
```

```python
config = BinanceThConfig()                       # from env / .env
config = BinanceThConfig(api_key="…", api_secret="…")   # or explicit
```

## Fields

Each field's env var is `BINANCE_TH_` + the uppercased name (e.g. `api_key` → `BINANCE_TH_API_KEY`).

| Field | Env var | Type | Default | Notes |
|-------|---------|------|---------|-------|
| `api_key` | `BINANCE_TH_API_KEY` | `str \| None` | `None` | Needed for signed + user-data endpoints. |
| `api_secret` | `BINANCE_TH_API_SECRET` | `SecretStr \| None` | `None` | Stored as `SecretStr`; read via `get_secret_value()`. |
| `rest_base_url` | `BINANCE_TH_REST_BASE_URL` | `str` | `https://api.binance.th` | REST host. |
| `ws_base_url` | `BINANCE_TH_WS_BASE_URL` | `str` | `wss://nbstream.binance.th/w3w/wsa/stream` | Reserved single-host stream; ACKs but does not push market data — **not** the market-stream default. Kept for forward-compat / user-data. |
| `ws_base_url_global` | `BINANCE_TH_WS_BASE_URL_GLOBAL` | `str` | `wss://www.binance.th/gstream` | Verified GLOBAL market-stream route. |
| `ws_base_url_site` | `BINANCE_TH_WS_BASE_URL_SITE` | `str` | `wss://www.binance.th/nstream` | Verified SITE market-stream route. |
| `timeout` | `BINANCE_TH_TIMEOUT` | `float` | `30.0` | Request timeout (s); `> 0`. |
| `max_retries` | `BINANCE_TH_MAX_RETRIES` | `int` | `3` | Retries for transient errors; `≥ 0`. |
| `enable_rate_limiting` | `BINANCE_TH_ENABLE_RATE_LIMITING` | `bool` | `True` | Automatic weight-based throttling. |
| `recv_window` | `BINANCE_TH_RECV_WINDOW` | `int` | `5000` | Signed-request validity window (ms); `> 0`, `≤ 60000`. |
| `ws_auto_reconnect` | `BINANCE_TH_WS_AUTO_RECONNECT` | `bool` | `True` | Reconnect dropped streams. |
| `ws_ping_interval` | `BINANCE_TH_WS_PING_INTERVAL` | `int` | `20` | WS ping interval (s); `> 0`. |
| `ws_ping_timeout` | `BINANCE_TH_WS_PING_TIMEOUT` | `int` | `10` | WS ping timeout (s); `> 0`. |
| `ws_supports_live_subscribe` | `BINANCE_TH_WS_SUPPORTS_LIVE_SUBSCRIBE` | `bool` | `True` | If `False`, dynamic (un)subscribe reconnects with a new `?streams=` URL. |
| `user_stream_keepalive_interval` | `BINANCE_TH_USER_STREAM_KEEPALIVE_INTERVAL` | `float` | `1200.0` | listenKey keepalive period (s); `> 0`, `< 1800` (under the 30-min expiry). |
| `log_level` | `BINANCE_TH_LOG_LEVEL` | `str` | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR`. |
| `log_requests` | `BINANCE_TH_LOG_REQUESTS` | `bool` | `False` | Log outgoing requests (debug). |
| `log_responses` | `BINANCE_TH_LOG_RESPONSES` | `bool` | `False` | Log responses (debug). |

## Methods

### has_credentials

```python
def has_credentials() -> bool
```
`True` when **both** `api_key` and `api_secret` are set. Use it to branch public-only vs signed flows.

### get_secret_value

```python
def get_secret_value() -> str | None
```
The plaintext API secret, or `None` if unset. This is the only place the secret is unwrapped — never log
its result.

## See Also

- [Authentication](../getting-started/authentication.md) · [GLOBAL vs SITE](../concepts/global-vs-site.md)
- [Rate limiting](../concepts/rate-limiting.md) · [WebSockets](../concepts/websockets.md)
