# MarketClient Reference

[หน้าแรก](../index.md) > อ้างอิง > market

[English](../../reference/market.md) · **ไทย**

**โมดูล:** `binance_th.market` · **มีให้ใช้ตั้งแต่:** 1.0.0

ข้อมูลตลาดสาธารณะ (`client.market`) ไม่ต้องใช้ credentials ทุก field ที่เป็นจำนวนเงินเป็นชนิด `Decimal`

## การ import

เข้าถึงผ่าน `client.market`

## เมธอด

### depth

```python
async def depth(symbol: str, *, limit: int | None = None) -> OrderBook
```
| พารามิเตอร์ | ชนิด | ค่าเริ่มต้น | คำอธิบาย |
|-----------|------|---------|-------------|
| `symbol` | `str` | — | เช่น `"BTCTHB"` |
| `limit` | `int \| None` | `None` | จำนวนระดับต่อฝั่ง |

**คืนค่า** `OrderBook` (`.last_update_id`, `.bids`, `.asks` — แต่ละตัวเป็น `OrderBookEntry` ที่มี `.price`/`.quantity`)

### trades

```python
async def trades(symbol: str, *, limit: int | None = None) -> list[Trade]
```
trade ล่าสุด **คืนค่า** `list[Trade]`

### agg_trades

```python
async def agg_trades(symbol: str, *, limit: int | None = None) -> list[AggregateTrade]
```
aggregate trade แบบบีบอัด **คืนค่า** `list[AggregateTrade]`

### klines

```python
async def klines(symbol: str, interval: KlineInterval | str, *,
                 limit: int | None = None, start_time: int | None = None,
                 end_time: int | None = None) -> list[Kline]
```
| พารามิเตอร์ | ชนิด | ค่าเริ่มต้น | คำอธิบาย |
|-----------|------|---------|-------------|
| `interval` | `KlineInterval \| str` | — | เช่น `KlineInterval.HOUR_1` หรือ `"1h"` |
| `limit` | `int \| None` | `None` | จำนวน candle สูงสุด |
| `start_time` / `end_time` | `int \| None` | `None` | epoch ms |

**คืนค่า** `list[Kline]` สำหรับช่วงข้อมูลยาว ๆ ให้ใช้ [`iter_klines`](#iter_klines)

### iter_klines

```python
async def iter_klines(symbol: str, interval: KlineInterval | str, *,
                      start_time: int, end_time: int, limit: int = 1000) -> AsyncIterator[Kline]
```
Async generator ที่ไล่ดึงข้อมูลทีละหน้าในช่วง `[start_time, end_time)` และตัดข้อมูลซ้ำโดยดูจาก open time โดย `start_time` และ
`end_time` นั้น **จำเป็นต้องระบุ** (epoch ms) ใช้งานด้วย `async for` — อย่า `await` การเรียกนี้ **ให้ค่า (yield)**
`Kline`

```python
candles = [k async for k in client.market.iter_klines("BTCTHB", "1h",
                                                       start_time=s, end_time=e)]
```

### ticker_price

```python
async def ticker_price(symbol: str) -> PriceTicker
```
ราคาล่าสุด **คืนค่า** `PriceTicker` (`.price: Decimal`)

### ticker_24hr

```python
async def ticker_24hr(symbol: str) -> Ticker24hr
```
สถิติแบบ rolling 24 ชั่วโมง **คืนค่า** `Ticker24hr` หมายเหตุ: มีหลาย field เป็น `null` สำหรับสัญลักษณ์แบบ SITE

### book_ticker

```python
async def book_ticker(symbol: str) -> BookTicker
```
bid/ask ที่ดีที่สุด **คืนค่า** `BookTicker` (`.bid_price`, `.bid_qty`, `.ask_price`, `.ask_qty`)

### reference_price

```python
async def reference_price(symbol: str) -> ReferencePrice
```
**เฉพาะสัญลักษณ์แบบ GLOBAL เท่านั้น** **อาจยก (raises)** `BinanceThBadRequestError` หากใช้กับสัญลักษณ์แบบ SITE/THB

### execution_rules

```python
async def execution_rules() -> ExecutionRules
```
กฎการเทรดของแต่ละสัญลักษณ์ **เฉพาะ GLOBAL เท่านั้น** **คืนค่า** `ExecutionRules` (`.get_symbol(sym)`)

## ดูเพิ่มเติม

- [คู่มือข้อมูลตลาด](../guides/market-data.md) · [คู่มือ Pagination](../guides/pagination.md)
- [models](models.md) · [GLOBAL vs SITE](../concepts/global-vs-site.md)
