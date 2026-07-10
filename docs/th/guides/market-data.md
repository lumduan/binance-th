# ข้อมูลตลาด

[หน้าแรก](../index.md) > คู่มือ > ข้อมูลตลาด

[English](../../guides/market-data.md) · **ไทย**

ทุกอย่างภายใต้ `client.market` เป็นสาธารณะ — ไม่ต้องใช้คีย์

## สิ่งที่ควรรู้ก่อน

- [การติดตั้ง](../getting-started/installation.md)
- [เงินและ Decimal](../concepts/money-and-decimals.md) — ราคาและปริมาณเป็น `Decimal`

---

## ดึง Order Book (snapshot)

```python
async with BinanceThClient() as client:
    book = await client.market.depth("BTCTHB", limit=20)
    print(book.last_update_id)
    print(book.bids[0].price, book.bids[0].quantity)   # best bid
    print(book.asks[0].price, book.asks[0].quantity)   # best ask
```

ถ้าอยากได้ Order Book ที่อัปเดตตลอด ให้ใช้ [Local Order Book](local-order-book.md) ผ่าน WebSocket แทน

## Trade ล่าสุดและ aggregate trade

```python
trades = await client.market.trades("BTCTHB", limit=50)
aggs = await client.market.agg_trades("BTCTHB", limit=50)
for t in trades[:3]:
    print(t.price, t.qty, "maker" if t.is_buyer_maker else "taker")
```

## Klines (แท่งเทียน)

```python
from binance_th import KlineInterval

candles = await client.market.klines("BTCTHB", KlineInterval.HOUR_1, limit=100)
for k in candles[:3]:
    print(k.open_time, k.open_price, k.high_price, k.low_price, k.close_price, k.volume)
```

`interval` รับได้ทั้ง enum `KlineInterval` หรือสตริงธรรมดาอย่าง `"1h"` สำหรับช่วงเวลายาว ๆ ที่เกินลิมิตต่อหนึ่งคำเรียก
ให้ใช้[การแบ่งหน้า](pagination.md) (`iter_klines`)

## Ticker

```python
last = await client.market.ticker_price("BTCTHB")     # ราคาล่าสุด
stats = await client.market.ticker_24hr("BTCTHB")      # สถิติ 24 ชั่วโมง
top = await client.market.book_ticker("BTCTHB")        # best bid/ask
print(last.price, stats.price_change_percent, top.bid_price, top.ask_price)
```

## Endpoint เฉพาะ GLOBAL

`reference_price` และ `execution_rules` มีเฉพาะสำหรับสัญลักษณ์ GLOBAL เท่านั้น การเรียกด้วยสัญลักษณ์ SITE/THB จะได้
`BinanceThBadRequestError`:

```python
ref = await client.market.reference_price("BTCUSDT")   # GLOBAL — โอเค
rules = await client.market.execution_rules()          # กฎของ GLOBAL
```

ดู [GLOBAL กับ SITE](../concepts/global-vs-site.md)

## ดูเพิ่มเติม

- [คู่มือ Local Order Book](local-order-book.md) — Order Book ที่ซิงก์ตัวเองผ่าน WebSocket
- [คู่มือ Market Streams](market-streams.md) — trade/แท่งเทียน/ticker แบบเรียลไทม์
- [อ้างอิง: market](../reference/market.md)
