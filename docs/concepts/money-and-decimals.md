# Money & Decimals

[Home](../index.md) > Concepts > Money & Decimals

**English** · [ไทย](../th/concepts/money-and-decimals.md)

Every monetary value in binance-th is a Python `Decimal` — prices, quantities, balances, fees, and
volumes. Nothing money-related is ever a `float`.

## Why

`float` can't represent most decimal fractions exactly, so `0.1 + 0.2 != 0.3`. For an order book or a
balance that's not acceptable — a rounding slip is real money. `Decimal` stores the exact value the
exchange sent.

## Pass Decimal in

When you place an order, use `Decimal` for price and quantity:

```python
from decimal import Decimal
from binance_th import OrderSide, OrderType, TimeInForce

order = await client.orders.create_order(
    "BTCTHB", OrderSide.BUY, OrderType.LIMIT,
    quantity=Decimal("0.001"),
    price=Decimal("2000000"),
    time_in_force=TimeInForce.GTC,
)
```

Build `Decimal` from a **string** (`Decimal("0.001")`), not a float (`Decimal(0.001)` inherits the
float's imprecision).

## And Decimal comes back out

```python
book = await client.market.depth("BTCTHB", limit=1)
best_bid_price, best_bid_qty = book.bids[0].price, book.bids[0].quantity
notional = best_bid_price * best_bid_qty        # Decimal arithmetic, exact
```

## On the wire

When the client sends an order it serializes `Decimal` as fixed-point text (`format(value, "f")`), never
scientific notation — so a small value like `0.00000003` goes out as `0.00000003`, not `3E-8`, which
also keeps the HMAC signature correct.

## See Also

- [Orders guide](../guides/orders.md) — validation snaps price/qty to the symbol's tick/step
- [Reference: models](../reference/models.md)
