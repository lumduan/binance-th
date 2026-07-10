# Errors & reconciliation

[Home](../index.md) > Concepts > Errors & reconciliation

**English** · [ไทย](../th/concepts/errors-and-reconciliation.md)

Every failure raises a typed exception, so you can catch exactly the case you care about. All of them
derive from `BinanceThError`.

## The hierarchy

```text
BinanceThError
├── BinanceThAPIError            (has status_code, request_id, response_data)
│   ├── BinanceThBadRequestError   400  bad params — fix the request
│   ├── BinanceThAuthError         401  bad key / signature / clock
│   ├── BinanceThWAFError          403  firewall block — back right off
│   ├── BinanceThIPBannedError     418  IP auto-banned after repeated 429s
│   ├── BinanceThRateLimitError    429  too many requests (retry_after, used_weight)
│   └── BinanceThServerError       5xx  server error — outcome UNKNOWN
├── BinanceThNetworkError        connection / DNS / TLS failure (usually transient)
├── BinanceThTimeoutError        request exceeded the configured timeout
├── BinanceThValidationError     client-side validation failed (field, value)
├── BinanceThWebSocketError      WS connect / parse / subscription failure
└── BinanceThOrderUnknownError   order sent, but its fate couldn't be confirmed
```

```python
from binance_th import BinanceThRateLimitError, BinanceThServerError

try:
    await client.orders.create_order(...)
except BinanceThRateLimitError as e:
    await asyncio.sleep(e.retry_after or 1)
```

## The one rule to internalize: a 5xx is *unknown*, not *failed*

When a request that changes state (like placing an order) gets a `5xx`, you **do not know** whether the
exchange applied it. Treating it as "failed" and blindly resubmitting can place the order twice.

So `BinanceThServerError` means *unknown*. For orders, the client goes further and reconciles for you.

## How order reconciliation works

`create_order` mints a client-order-id **before** it sends the request. If the create then hits a
`5xx`, a timeout, or a network error, the client queries the order **by that id**:

- The order is found → it's returned as if the create had succeeded.
- The server says "unknown order" (`-2013`) → it was definitely not placed →
  `BinanceThOrderUnknownError(resubmittable=True)`.
- The reconcile query itself fails → `BinanceThOrderUnknownError(resubmittable=False)` — genuinely
  unknown; **do not** blindly resubmit.

```python
from binance_th import BinanceThOrderUnknownError

try:
    order = await client.orders.create_order(...)
except BinanceThOrderUnknownError as e:
    if e.resubmittable:
        order = await client.orders.create_order(...)   # confirmed not placed — safe to retry
    else:
        # check the order's state before doing anything else
        ...
```

The client never does a second POST on its own — reconciliation is query-only.

## See Also

- [Orders guide](../guides/orders.md)
- [Rate limiting](rate-limiting.md) — how 429/418 are surfaced
- [Reference: exceptions](../reference/exceptions.md)
