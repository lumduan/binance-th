# OrdersClient Reference

[Home](../index.md) > Reference > orders

**English** · [ไทย](../th/reference/orders.md)

**Module:** `binance_th.orders` · **Available since:** 1.0.0

Signed order management (`client.orders`) — create, cancel, and query orders. Every method is **signed**
and `create_order`/`cancel_order` are **mutating**. Prices and quantities are `Decimal`.

> ⚠ **Reconciliation.** A `5xx` from the exchange means the outcome is **UNKNOWN**, not failed — the
> order may or may not have been accepted. Do not blindly resubmit; query state first. See
> [Errors & reconciliation](../concepts/errors-and-reconciliation.md).

## Import

Accessed as `client.orders`. Requires credentials.

## Methods

### create_order

```python
async def create_order(symbol: str | None = None, side: OrderSide | str | None = None,
                       order_type: OrderType | str | None = None, *,
                       request: OrderRequest | None = None,
                       quantity: Decimal | None = None,
                       price: Decimal | None = None,
                       time_in_force: TimeInForce | str | None = None,
                       quote_order_qty: Decimal | None = None,
                       stop_price: Decimal | None = None,
                       new_client_order_id: str | None = None,
                       recv_window: int | None = None,
                       validate: bool = True) -> Order
```
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | `str \| None` | `None` | e.g. `"BTCTHB"`; required unless `request=` supplies it |
| `side` | `OrderSide \| str \| None` | `None` | `BUY` / `SELL` |
| `order_type` | `OrderType \| str \| None` | `None` | `LIMIT`, `MARKET`, `STOP_LOSS_LIMIT`, … |
| `request` | `OrderRequest \| None` | `None` | a prebuilt validated request (used instead of the kwargs below) |
| `quantity` | `Decimal \| None` | `None` | base-asset amount |
| `price` | `Decimal \| None` | `None` | required for `LIMIT` |
| `time_in_force` | `TimeInForce \| str \| None` | `None` | `GTC` / `IOC` / `FOK`; required for `LIMIT` |
| `quote_order_qty` | `Decimal \| None` | `None` | `MARKET` alternative to `quantity` |
| `stop_price` | `Decimal \| None` | `None` | required for `STOP_*` types |
| `new_client_order_id` | `str \| None` | `None` | your idempotency id (auto-minted if omitted) |
| `recv_window` | `int \| None` | `None` | override the config `recv_window` |
| `validate` | `bool` | `True` | run client-side rule checks before sending |

**Signed. Mutating.** Client-side validation mirrors Binance's rules (LIMIT ⇒ price + timeInForce;
MARKET ⇒ quantity **or** quoteOrderQty; STOP\* ⇒ stopPrice). **Returns** `Order`. **Raises**
`BinanceThValidationError` (rules), `BinanceThAuthError` (credentials), `BinanceThServerError`
(5xx → UNKNOWN).

```python
from binance_th import OrderSide, OrderType, TimeInForce

order = await client.orders.create_order(
    "BTCTHB", OrderSide.BUY, OrderType.LIMIT,
    quantity="0.001", price="2000000", time_in_force=TimeInForce.GTC,
)
print(order.order_id, order.status)
```

### cancel_order

```python
async def cancel_order(symbol: str, *, order_id: int | None = None,
                       orig_client_order_id: str | None = None,
                       recv_window: int | None = None) -> Order
```
**Signed. Mutating.** Pass **`order_id` or `orig_client_order_id`** (at least one). **Returns** the
canceled `Order`. **Raises** `BinanceThValidationError` if neither id is given.

### query_order

```python
async def query_order(symbol: str, *, order_id: int | None = None,
                      orig_client_order_id: str | None = None,
                      recv_window: int | None = None) -> Order
```
**Signed.** Read one order's current state (use it to reconcile after a 5xx). Pass **`order_id` or
`orig_client_order_id`**. **Returns** `Order`.

### open_orders

```python
async def open_orders(symbol: str | None = None) -> list[Order]
```
**Signed.** All open orders, optionally filtered by `symbol`. **Returns** `list[Order]`.

## See Also

- [Orders guide](../guides/orders.md) — validation, id minting, UNKNOWN reconciliation
- [Errors & reconciliation](../concepts/errors-and-reconciliation.md) · [models](models.md)
- [user-stream](user-stream.md) — follow order updates in real time
