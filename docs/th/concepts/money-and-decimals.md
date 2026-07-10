# เงินและ Decimal

[หน้าแรก](../index.md) > แนวคิด > เงินและ Decimal

[English](../../concepts/money-and-decimals.md) · **ไทย**

ทุกค่าที่เป็นเงินใน binance-th เป็น `Decimal` ของ Python — ราคา ปริมาณ ยอดคงเหลือ ค่าธรรมเนียม และปริมาณซื้อขาย
ไม่มีอะไรที่เกี่ยวกับเงินเป็น `float` เลย

## ทำไม

`float` แทนเศษทศนิยมส่วนใหญ่ได้ไม่ตรงเป๊ะ จึงทำให้ `0.1 + 0.2 != 0.3` สำหรับ Order Book หรือยอดคงเหลือ นั่นรับไม่ได้ —
ความคลาดเคลื่อนจากการปัดเศษคือเงินจริง ๆ ส่วน `Decimal` เก็บค่าที่ตรงกับที่ตลาดส่งมาเป๊ะ

## ส่ง Decimal เข้าไป

เวลาส่งออเดอร์ ให้ใช้ `Decimal` สำหรับราคาและปริมาณ:

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

สร้าง `Decimal` จาก **สตริง** (`Decimal("0.001")`) ไม่ใช่จาก float (`Decimal(0.001)` จะรับความคลาดเคลื่อนของ float ติดมาด้วย)

## และ Decimal ก็คืนกลับออกมา

```python
book = await client.market.depth("BTCTHB", limit=1)
best_bid_price, best_bid_qty = book.bids[0].price, book.bids[0].quantity
notional = best_bid_price * best_bid_qty        # คำนวณด้วย Decimal แม่นยำเป๊ะ
```

## บนสาย (on the wire)

เวลาไคลเอนต์ส่งออเดอร์ มันจะแปลง `Decimal` เป็นข้อความแบบจุดตรึง (`format(value, "f")`) ไม่ใช่รูปวิทยาศาสตร์ —
ดังนั้นค่าน้อย ๆ อย่าง `0.00000003` จะออกไปเป็น `0.00000003` ไม่ใช่ `3E-8` ซึ่งยังช่วยให้ signature แบบ HMAC ถูกต้องด้วย

## ดูเพิ่มเติม

- [คู่มือออเดอร์](../guides/orders.md) — validation จะปรับราคา/ปริมาณให้เข้ากับ tick/step ของสัญลักษณ์
- [อ้างอิง: models](../reference/models.md)
