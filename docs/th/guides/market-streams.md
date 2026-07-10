# Market Streams

[หน้าแรก](../index.md) > คู่มือ > Market Streams

[English](../../guides/market-streams.md) · **ไทย**

`client.ws` ให้ข้อมูลตลาดแบบเรียลไทม์ผ่าน WebSocket ในรูปของ async iterator ทั้งหมดเป็นสาธารณะ — ไม่ต้องใช้คีย์

## สิ่งที่ควรรู้ก่อน

- [เริ่มต้นอย่างรวดเร็ว](../getting-started/quickstart.md)
- [WebSocket](../concepts/websockets.md) — การเชื่อมต่อใหม่และการจัดเส้นทาง

---

## Iterator ตระกูล `watch_*`

แต่ละตัวคืน async iterator ของเหตุการณ์ที่มีชนิดชัดเจน — วนด้วย `async for`:

| เมธอด | คืนค่า |
|--------|--------|
| `client.ws.watch_depth(symbol)` | `DepthUpdateEvent` (diff-depth ดิบ) |
| `client.ws.watch_trades(symbol)` | `TradeEvent` |
| `client.ws.watch_agg_trades(symbol)` | `AggTradeEvent` |
| `client.ws.watch_klines(symbol, interval="1m")` | `KlineEvent` |
| `client.ws.watch_book_ticker(symbol)` | `BookTickerEvent` |
| `client.ws.watch_ticker(symbol)` | `TickerEvent` |

```python
async with BinanceThClient() as client:
    async for trade in client.ws.watch_trades("BTCTHB"):
        print(trade.price, trade.quantity)
```

## แท่งเทียน

```python
async for k in client.ws.watch_klines("BTCTHB", "1m"):
    if k.kline.is_closed:                 # ทำเฉพาะแท่งที่ปิด (finalized) แล้ว
        print(k.kline.close_price, k.kline.volume)
```

## ดูหลาย stream พร้อมกัน

เปิดแต่ละ iterator เป็น task:

```python
import asyncio

async def pump(agen, label):
    async for evt in agen:
        print(label, evt)

async with BinanceThClient() as client:
    await asyncio.gather(
        pump(client.ws.watch_trades("BTCTHB"), "trade"),
        pump(client.ws.watch_book_ticker("BTCTHB"), "book"),
    )
```

ไคลเอนต์จะรวม (multiplex) พวกมันลงบนการเชื่อมต่อให้น้อยที่สุดเท่าที่ทำได้ (หนึ่งต่อโฮสต์)

## การหยุด

การ break ออกจากลูปจะ unsubscribe stream นั้น ส่วนการออกจาก `async with` (หรือ `await client.ws.aclose()`)
จะปิดการเชื่อมต่อให้เรียบร้อย การเชื่อมต่อใหม่ระหว่างสตรีมเป็นแบบอัตโนมัติ — ดู [WebSocket](../concepts/websockets.md)

## Depth เทียบกับ Order Book ที่ซิงก์แล้ว

`watch_depth` ให้เหตุการณ์ diff-depth ดิบ ถ้าสิ่งที่คุณต้องการจริง ๆ คือ Order Book ที่อัปเดตอยู่เสมอ
ให้ใช้ [`order_book`](local-order-book.md) — มันจะเอา diff เหล่านั้นไปใช้กับ snapshot ทาง REST ให้คุณ

## ดูเพิ่มเติม

- [คู่มือ Local Order Book](local-order-book.md)
- [อ้างอิง: streams](../reference/streams.md)
