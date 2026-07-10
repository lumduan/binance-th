# Orders

[Home](../index.md) > Guides > Orders

**English** · [ไทย](../th/guides/orders.md)

`client.orders` places, cancels, and queries orders. These are **signed** endpoints that move **real
money** — read [Errors & reconciliation](../concepts/errors-and-reconciliation.md) first.

## Prerequisites

- [Authentication](../getting-started/authentication.md) — needs `api_key` + `api_secret`
- [Money & Decimals](../concepts/money-and-decimals.md)

> ⚠ The order response models are ⚠ASSUMED (mock-tested, not verified against a live fill). See
> [Assumed shapes](../concepts/assumed-shapes.md).

---

## Place a limit order

```python
from decimal import Decimal
from binance_th import OrderSide, OrderType, TimeInForce

order = await client.orders.create_order(
    "BTCTHB", OrderSide.BUY, OrderType.LIMIT,
    quantity=Decimal("0.001"),
    price=Decimal("2000000"),
    time_in_force=TimeInForce.GTC,
)
print(order.order_id, order.status)
```

`side`/`order_type`/`time_in_force` accept the enum or a string (`"BUY"`, `"LIMIT"`, `"GTC"`).

### Market orders

```python
# by base quantity …
await client.orders.create_order("BTCTHB", OrderSide.BUY, OrderType.MARKET,
                                 quantity=Decimal("0.001"))
# … or by quote amount (spend N THB)
await client.orders.create_order("BTCTHB", OrderSide.BUY, OrderType.MARKET,
                                 quote_order_qty=Decimal("500"))
```

## Validation happens before anything is sent

By default (`validate=True`) the client checks the order against the symbol's exchange-info filters and
**snaps** price to the tick size and quantity to the step size, and enforces min/max price, min/max
quantity, and `MIN_NOTIONAL` — raising `BinanceThValidationError(field=…, value=…)` locally so a bad
order never reaches the exchange. Pass `validate=False` to skip it (the server remains the final judge).

## Build the request object yourself

Instead of the keyword fields you can pass a prebuilt `OrderRequest` — but not both:

```python
from binance_th.models import OrderRequest

req = OrderRequest(symbol="BTCTHB", side="BUY", order_type="LIMIT",
                   quantity=Decimal("0.001"), price=Decimal("2000000"), time_in_force="GTC")
order = await client.orders.create_order(request=req)
```

## Cancel and query

Identify an order by `order_id` **or** `orig_client_order_id` (one of them):

```python
await client.orders.cancel_order("BTCTHB", order_id=order.order_id)
same = await client.orders.query_order("BTCTHB", order_id=order.order_id)
opens = await client.orders.open_orders("BTCTHB")     # or open_orders() for all symbols
```

## The 5xx-UNKNOWN safety net

`create_order` mints a client-order-id before sending, so if the create hits a `5xx`/timeout it can
reconcile by that id rather than risk a double-place. Handle the unknown case:

```python
from binance_th import BinanceThOrderUnknownError

try:
    order = await client.orders.create_order(...)
except BinanceThOrderUnknownError as e:
    if e.resubmittable:      # confirmed NOT placed
        order = await client.orders.create_order(...)
    # else: genuinely unknown — inspect state before acting
```

Full explanation in [Errors & reconciliation](../concepts/errors-and-reconciliation.md).

## See Also

- [User-data stream guide](user-data-stream.md) — watch your orders update live
- [Reference: orders](../reference/orders.md)
