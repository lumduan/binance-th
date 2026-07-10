# ออเดอร์

[หน้าแรก](../index.md) > คู่มือ > ออเดอร์

[English](../../guides/orders.md) · **ไทย**

`client.orders` ใช้ส่ง ยกเลิก และสอบถามออเดอร์ ทั้งหมดนี้เป็น endpoint แบบ **signed** ที่ขยับ **เงินจริง** —
อ่าน[ข้อผิดพลาดและการกระทบยอด](../concepts/errors-and-reconciliation.md)ก่อน

## สิ่งที่ควรรู้ก่อน

- [การยืนยันตัวตน](../getting-started/authentication.md) — ต้องใช้ `api_key` + `api_secret`
- [เงินและ Decimal](../concepts/money-and-decimals.md)

> ⚠ โมเดล response ของออเดอร์เป็น ⚠ASSUMED (ทดสอบด้วย mock เท่านั้น ยังไม่ยืนยันกับการ fill จริง) ดู
> [รูปร่างที่ยังไม่ยืนยัน](../concepts/assumed-shapes.md)

---

## ส่ง limit order

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

`side`/`order_type`/`time_in_force` รับได้ทั้ง enum หรือสตริง (`"BUY"`, `"LIMIT"`, `"GTC"`)

### Market order

```python
# ตามปริมาณ base …
await client.orders.create_order("BTCTHB", OrderSide.BUY, OrderType.MARKET,
                                 quantity=Decimal("0.001"))
# … หรือตามจำนวนเงิน quote (ใช้ N THB)
await client.orders.create_order("BTCTHB", OrderSide.BUY, OrderType.MARKET,
                                 quote_order_qty=Decimal("500"))
```

## Validation เกิดก่อนที่จะส่งอะไรออกไป

โดยปริยาย (`validate=True`) ไคลเอนต์จะตรวจออเดอร์กับ filter จาก exchange-info ของสัญลักษณ์ และ **snap** ราคาให้เข้ากับ
tick size และปริมาณให้เข้ากับ step size พร้อมบังคับ min/max ของราคา, min/max ของปริมาณ และ `MIN_NOTIONAL` —
โดยยก `BinanceThValidationError(field=…, value=…)` ในเครื่องเพื่อให้ออเดอร์ที่ผิดไม่มีวันไปถึงตลาด ใส่ `validate=False`
เพื่อข้ามขั้นตอนนี้ (เซิร์ฟเวอร์ยังเป็นผู้ตัดสินสุดท้ายอยู่ดี)

## ประกอบ request object เอง

แทนที่จะใช้ฟิลด์แบบ keyword คุณส่ง `OrderRequest` ที่ประกอบไว้ล่วงหน้าได้ — แต่ใช้พร้อมกันทั้งสองอย่างไม่ได้:

```python
from binance_th.models import OrderRequest

req = OrderRequest(symbol="BTCTHB", side="BUY", order_type="LIMIT",
                   quantity=Decimal("0.001"), price=Decimal("2000000"), time_in_force="GTC")
order = await client.orders.create_order(request=req)
```

## ยกเลิกและสอบถาม

ระบุออเดอร์ด้วย `order_id` **หรือ** `orig_client_order_id` (อย่างใดอย่างหนึ่ง):

```python
await client.orders.cancel_order("BTCTHB", order_id=order.order_id)
same = await client.orders.query_order("BTCTHB", order_id=order.order_id)
opens = await client.orders.open_orders("BTCTHB")     # หรือ open_orders() สำหรับทุกสัญลักษณ์
```

## ตาข่ายนิรภัย 5xx-UNKNOWN

`create_order` จะสร้าง client-order-id ก่อนส่ง ดังนั้นถ้าการสร้างไปเจอ `5xx`/timeout มันจะกระทบยอดด้วย id นั้นได้
แทนที่จะเสี่ยงวางซ้ำ จัดการกรณีไม่ทราบผลแบบนี้:

```python
from binance_th import BinanceThOrderUnknownError

try:
    order = await client.orders.create_order(...)
except BinanceThOrderUnknownError as e:
    if e.resubmittable:      # ยืนยันแล้วว่ายังไม่ได้วาง
        order = await client.orders.create_order(...)
    # else: ไม่ทราบผลจริง ๆ — ตรวจสถานะก่อนทำอะไรต่อ
```

คำอธิบายเต็มอยู่ที่[ข้อผิดพลาดและการกระทบยอด](../concepts/errors-and-reconciliation.md)

## ดูเพิ่มเติม

- [คู่มือ User-data stream](user-data-stream.md) — ดูออเดอร์ของคุณอัปเดตแบบเรียลไทม์
- [อ้างอิง: orders](../reference/orders.md)
