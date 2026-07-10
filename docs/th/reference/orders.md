# OrdersClient Reference

[หน้าแรก](../index.md) > อ้างอิง > orders

[English](../../reference/orders.md) · **ไทย**

**โมดูล:** `binance_th.orders` · **มีให้ใช้ตั้งแต่:** 1.0.0

การจัดการออเดอร์แบบ signed (`client.orders`) — สร้าง ยกเลิก และ query ออเดอร์ ทุกเมธอดเป็นแบบ **signed**
และ `create_order`/`cancel_order` เป็นแบบ **mutating** ราคาและปริมาณเป็น `Decimal`

> ⚠ **กระทบยอด.** `5xx` จาก exchange หมายความว่าผลลัพธ์เป็น **UNKNOWN** ไม่ใช่ล้มเหลว —
> ออเดอร์อาจถูกรับหรือไม่ถูกรับก็ได้ อย่าส่งซ้ำแบบมั่ว ๆ ให้ query สถานะก่อน ดู
> [Errors & reconciliation](../concepts/errors-and-reconciliation.md)

## การ import

เข้าถึงผ่าน `client.orders` ต้องใช้ credentials

## เมธอด

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
| พารามิเตอร์ | ชนิด | ค่าเริ่มต้น | คำอธิบาย |
|-----------|------|---------|-------------|
| `symbol` | `str \| None` | `None` | เช่น `"BTCTHB"`; จำเป็น เว้นแต่ `request=` จะระบุมาให้ |
| `side` | `OrderSide \| str \| None` | `None` | `BUY` / `SELL` |
| `order_type` | `OrderType \| str \| None` | `None` | `LIMIT`, `MARKET`, `STOP_LOSS_LIMIT`, … |
| `request` | `OrderRequest \| None` | `None` | request ที่ build ไว้ล่วงหน้าและ validate แล้ว (ใช้แทน kwargs ด้านล่าง) |
| `quantity` | `Decimal \| None` | `None` | จำนวนของ base asset |
| `price` | `Decimal \| None` | `None` | จำเป็นสำหรับ `LIMIT` |
| `time_in_force` | `TimeInForce \| str \| None` | `None` | `GTC` / `IOC` / `FOK`; จำเป็นสำหรับ `LIMIT` |
| `quote_order_qty` | `Decimal \| None` | `None` | ทางเลือกแทน `quantity` สำหรับ `MARKET` |
| `stop_price` | `Decimal \| None` | `None` | จำเป็นสำหรับชนิด `STOP_*` |
| `new_client_order_id` | `str \| None` | `None` | id สำหรับ idempotency ของคุณ (สร้างให้อัตโนมัติถ้าไม่ระบุ) |
| `recv_window` | `int \| None` | `None` | override ค่า `recv_window` ใน config |
| `validate` | `bool` | `True` | ตรวจสอบกฎฝั่ง client ก่อนส่ง |

**Signed (ต้องเซ็น). Mutating (เปลี่ยนสถานะ).** การ validate ฝั่ง client สะท้อนกฎของ Binance (LIMIT ⇒ price + timeInForce;
MARKET ⇒ quantity **หรือ** quoteOrderQty; STOP\* ⇒ stopPrice) **คืนค่า** `Order` **อาจยก (raises)**
`BinanceThValidationError` (ผิดกฎ), `BinanceThAuthError` (credentials), `BinanceThServerError`
(5xx → UNKNOWN)

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
**Signed (ต้องเซ็น). Mutating (เปลี่ยนสถานะ).** ส่ง **`order_id` หรือ `orig_client_order_id`** (อย่างน้อยหนึ่งตัว) **คืนค่า** `Order`
ที่ถูกยกเลิก **อาจยก (raises)** `BinanceThValidationError` ถ้าไม่ได้ระบุ id มาเลยสักตัว

### query_order

```python
async def query_order(symbol: str, *, order_id: int | None = None,
                      orig_client_order_id: str | None = None,
                      recv_window: int | None = None) -> Order
```
**Signed (ต้องเซ็น).** อ่านสถานะปัจจุบันของออเดอร์หนึ่งตัว (ใช้กระทบยอดหลังเจอ 5xx) ส่ง **`order_id` หรือ
`orig_client_order_id`** **คืนค่า** `Order`

### open_orders

```python
async def open_orders(symbol: str | None = None) -> list[Order]
```
**Signed (ต้องเซ็น).** ออเดอร์ที่เปิดอยู่ทั้งหมด จะกรองด้วย `symbol` ก็ได้ **คืนค่า** `list[Order]`

## ดูเพิ่มเติม

- [คู่มือ orders](../guides/orders.md) — การ validate, การสร้าง id, การกระทบยอด UNKNOWN
- [ข้อผิดพลาดและการกระทบยอด](../concepts/errors-and-reconciliation.md) · [models](models.md)
- [user-stream](user-stream.md) — ติดตามการอัปเดตออเดอร์แบบเรียลไทม์
