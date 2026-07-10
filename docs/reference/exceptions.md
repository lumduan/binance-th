# Exceptions Reference

[Home](../index.md) > Reference > exceptions

**Module:** `binance_th.exceptions` · **Available since:** 1.0.0

Every error the library raises. Catch `BinanceThError` to catch them all; catch a specific subclass to
handle one case.

## Import

```python
from binance_th.exceptions import (
    BinanceThError, BinanceThAPIError, BinanceThRateLimitError, BinanceThServerError,
    BinanceThOrderUnknownError,  # …and the rest below
)
```

## Hierarchy

```text
BinanceThError                     (message, code=None, details=None)
├── BinanceThAPIError              adds status_code, request_id, response_data
│   ├── BinanceThBadRequestError   400
│   ├── BinanceThAuthError         401
│   ├── BinanceThWAFError          403
│   ├── BinanceThIPBannedError     418   adds retry_after
│   ├── BinanceThRateLimitError    429   adds retry_after, used_weight, limit_weight
│   └── BinanceThServerError       5xx   execution status UNKNOWN — not failure
├── BinanceThNetworkError
├── BinanceThTimeoutError          adds timeout
├── BinanceThValidationError       adds field, value  (client-side, pre-send)
├── BinanceThWebSocketError
└── BinanceThOrderUnknownError     adds client_order_id, symbol, resubmittable
```

## Attributes

`BinanceThError` (base): `message: str`, `code: int | None`, `details: dict`. `str(err)` renders
`"[code] message"` when a code is set.

| Exception | Extra attributes | Raised when |
|-----------|------------------|-------------|
| `BinanceThAPIError` | `status_code`, `request_id`, `response_data` | any non-2xx the map below doesn't specialise |
| `BinanceThBadRequestError` | (from API error) | `400` — malformed request; fix params before resend |
| `BinanceThAuthError` | (from API error) | `401` — bad/missing key, signature, or timestamp |
| `BinanceThWAFError` | (from API error) | `403` — firewall block; stop and review |
| `BinanceThIPBannedError` | `retry_after` | `418` — IP auto-banned after repeated 429s |
| `BinanceThRateLimitError` | `retry_after`, `used_weight`, `limit_weight` | `429` — back off `retry_after` seconds |
| `BinanceThServerError` | (from API error) | `5xx` — **UNKNOWN** outcome; reconcile, don't assume failure |
| `BinanceThNetworkError` | — | DNS/connection/TLS failure (transient) |
| `BinanceThTimeoutError` | `timeout` | request exceeded the configured timeout |
| `BinanceThValidationError` | `field`, `value` | client-side validation failed before sending |
| `BinanceThWebSocketError` | — | WS connect/parse/subscribe failure (planned reconnects don't raise) |
| `BinanceThOrderUnknownError` | `client_order_id`, `symbol`, `resubmittable` | an order create hit 5xx/timeout/network and reconciliation could not confirm it |

`BinanceThOrderUnknownError.resubmittable` is `True` **only** when the reconciliation query positively
confirmed the order was *not* placed. If it is `False`, the status is genuinely unknown — do not blindly
resubmit.

## Helpers

```python
HTTP_STATUS_MAP: dict[int, type[BinanceThAPIError]]
def get_exception_for_status_code(status_code: int) -> type[BinanceThAPIError]
```
`get_exception_for_status_code` returns the class for a status code (any `>= 500` → `BinanceThServerError`;
unknown 4xx → `BinanceThAPIError`).

## Example

```python
from binance_th.exceptions import BinanceThRateLimitError, BinanceThServerError

try:
    order = await client.orders.create_order(...)
except BinanceThRateLimitError as e:
    await asyncio.sleep(e.retry_after or 1)
except BinanceThServerError:
    order = await client.orders.query_order("BTCTHB", orig_client_order_id=my_id)  # reconcile
```

## See Also

- [Errors & reconciliation](../concepts/errors-and-reconciliation.md) · [Orders guide](../guides/orders.md)
- [Rate limiting](../concepts/rate-limiting.md)
