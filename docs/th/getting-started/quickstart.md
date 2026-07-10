# เริ่มต้นอย่างรวดเร็ว

[หน้าแรก](../index.md) > เริ่มต้นใช้งาน > เริ่มต้นอย่างรวดเร็ว

[English](../../getting-started/quickstart.md) · **ไทย**

หน้านี้พาไล่ทีละขั้นผ่านสคริปต์ที่สมบูรณ์ — ข้อมูลสาธารณะ Order Book แบบเรียลไทม์ และ stream การเทรด โดยไม่ต้องใช้ API key

## ไคลเอนต์เป็น async context manager

`BinanceThClient` เป็นเจ้าของการเชื่อมต่อ HTTP และ WebSocket ของตัวเอง ฉะนั้นให้เปิดด้วย `async with` เสมอ
เมื่อออกจากบล็อกมันจะปิดทุกอย่างให้เอง

```python
import asyncio
from binance_th import BinanceThClient

async def main() -> None:
    async with BinanceThClient() as client:
        pong = await client.ping()
        print("เชื่อมต่อได้:", pong)

asyncio.run(main())
```

## อ่านข้อมูลตลาด (REST)

```python
async with BinanceThClient() as client:
    book = await client.market.depth("BTCTHB", limit=5)
    print("best bid:", book.bids[0].price, book.bids[0].quantity)

    last = await client.market.ticker_price("BTCTHB")
    print("ราคาล่าสุด:", last.price)   # เป็น Decimal
```

ราคาและปริมาณเป็น `Decimal` — ดู[เงินและ Decimal](../concepts/money-and-decimals.md)

## ติดตาม Order Book แบบเรียลไทม์ (WebSocket)

`client.ws.order_book(...)` คืน Order Book ที่เริ่มจาก snapshot ผ่าน REST แล้วอัปเดตตัวเองให้ทันสมัยตลอดจาก stream depth
คุณอ่านค่าจากมันแบบซิงโครนัส ส่วนตัวมันอัปเดตอยู่เบื้องหลัง

```python
async with BinanceThClient() as client:
    order_book = await client.ws.order_book("BTCTHB")
    await order_book.wait_synced()          # snapshot แรกถูกใช้แล้ว
    print("best bid:", order_book.best_bid())
    print("3 ask บนสุด:", order_book.asks(3))
    await order_book.aclose()               # หยุดการซิงก์เบื้องหลัง
```

## stream การเทรด (WebSocket)

เมธอด `watch_*` เป็น async iterator — วนอ่านด้วย `async for`

```python
async with BinanceThClient() as client:
    async for trade in client.ws.watch_trades("BTCTHB"):
        print(trade.price, trade.quantity, "maker" if trade.is_buyer_maker else "taker")
        break   # เอาอันเดียวแล้วหยุด
```

## ขั้นถัดไป

- เพิ่มคีย์เพื่ออ่านข้อมูลบัญชี ส่งออเดอร์ และใช้ user-data stream:
  [การยืนยันตัวตน](authentication.md)
- ทำความเข้าใจการแยกสัญลักษณ์เฉพาะของไทย: [GLOBAL กับ SITE](../concepts/global-vs-site.md)
- ดูทุกอย่างแบบแยกตามงานใน[คู่มือ](../guides/market-data.md)

## ดูเพิ่มเติม

- [คู่มือข้อมูลตลาด](../guides/market-data.md)
- [คู่มือ Local Order Book](../guides/local-order-book.md)
- [เอกสารอ้างอิง API](../reference/index.md)
