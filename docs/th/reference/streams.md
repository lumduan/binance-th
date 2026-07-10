# StreamClient Reference

[หน้าแรก](../index.md) > อ้างอิง > streams

[English](../../reference/streams.md) · **ไทย**

**โมดูล:** `binance_th.ws` · **มีให้ใช้ตั้งแต่:** 1.0.0

stream ข้อมูลตลาดผ่าน WebSocket (`client.ws`) สาธารณะ — ไม่ต้องใช้ credentials แต่ละ `watch_*` เป็น **async
generator** ที่คุณ consume ด้วย `async for`; การเชื่อมต่อจะ reconnect ให้อัตโนมัติ และยัง build
[`ManagedOrderBook`](#managedorderbook) ที่ sync ตัวเองได้ด้วย

## การ import

เข้าถึงผ่าน `client.ws`

## เมธอด

ทุก `watch_*` เป็น async generator ที่ yield typed event ออกมาเรื่อย ๆ จนกว่าคุณจะ `break` หรือ client ปิดการเชื่อมต่อ
วนด้วย `async for` — อย่า `await` ตัวการเรียกเอง

### watch_depth

```python
async def watch_depth(symbol: str) -> AsyncIterator[DepthUpdateEvent]
```
diff ของ Order Book แบบ incremental ถ้าอยากได้ book ที่ดูแล sync ให้อัตโนมัติ ให้ใช้ [`order_book`](#order_book) แทน

### watch_trades

```python
async def watch_trades(symbol: str) -> AsyncIterator[TradeEvent]
```
trade แบบเรียลไทม์

```python
async with BinanceThClient() as client:
    async for t in client.ws.watch_trades("BTCTHB"):
        print(t.price, t.quantity)
        break
```

### watch_agg_trades

```python
async def watch_agg_trades(symbol: str) -> AsyncIterator[AggTradeEvent]
```
aggregate trade แบบเรียลไทม์

### watch_klines

```python
async def watch_klines(symbol: str, interval: str = "1m") -> AsyncIterator[KlineEvent]
```
| พารามิเตอร์ | ชนิด | ค่าเริ่มต้น | คำอธิบาย |
|-----------|------|---------|-------------|
| `interval` | `str` | `"1m"` | ช่วงเวลาของแท่งเทียน เช่น `"1m"`, `"1h"` (ใช้ `KlineInterval` ก็ได้ — มันเป็น `str`) |

แท่งเทียนแบบเรียลไทม์; `.is_closed` ของแต่ละ event บอกว่าเป็น tick สุดท้ายของแท่งนั้น

### watch_book_ticker

```python
async def watch_book_ticker(symbol: str) -> AsyncIterator[BookTickerEvent]
```
best bid/ask ทุกครั้งที่มีการเปลี่ยนแปลง

### watch_ticker

```python
async def watch_ticker(symbol: str) -> AsyncIterator[TickerEvent]
```
อัปเดต ticker แบบ rolling 24 ชั่วโมง

### order_book

```python
async def order_book(symbol: str, *, limit: int = 1000) -> ManagedOrderBook
```
| พารามิเตอร์ | ชนิด | ค่าเริ่มต้น | คำอธิบาย |
|-----------|------|---------|-------------|
| `limit` | `int` | `1000` | depth ของ REST snapshot ที่ใช้ seed book เริ่มต้น |

**ต้อง await ก่อน** คืน [`ManagedOrderBook`](#managedorderbook) — book ในเครื่องที่ถูก sync ให้ตรงกันจาก REST
snapshot บวกกับ depth diff stream ยังไม่เริ่มทำงาน; ให้เรียก `start()`

### aclose

```python
async def aclose() -> None
```
ปิด stream ที่เปิดอยู่ทั้งหมดและ managed book ทั้งหมด `client.aclose()` จะเรียกให้คุณเอง

---

## ManagedOrderBook

**มีให้ใช้ตั้งแต่:** 1.0.0. A local order book that seeds from a REST snapshot and stays current from the
depth-diff stream. `Level` is `tuple[Decimal, Decimal]` — `(price, quantity)`.

### start

```python
async def start() -> None
```
เริ่ม sync (snapshot + replay diff) ในเบื้องหลัง เรียกครั้งเดียว

### synced

```python
synced: bool  # property
```
เป็น `True` เมื่อ snapshot และ diff stream ถูกกระทบยอดตรงกันแล้ว

### wait_synced

```python
async def wait_synced() -> None
```
await จนกว่า `synced` จะเป็น `True`

### best_bid / best_ask

```python
def best_bid() -> Level | None
def best_ask() -> Level | None
```
level บนสุดของแต่ละฝั่ง หรือ `None` ถ้ายังไม่ sync

### bids / asks

```python
def bids(n: int = 10) -> list[Level]
def asks(n: int = 10) -> list[Level]
```
level สูงสุด `n` อันดับแรก เรียงจากดีที่สุดก่อน

### aclose

```python
async def aclose() -> None
```
หยุด sync และปล่อย stream

```python
book = await client.ws.order_book("BTCTHB")
await book.start()
await book.wait_synced()
print(book.best_bid(), book.best_ask())
await book.aclose()
```

## ดูเพิ่มเติม

- [Market streams guide](../guides/market-streams.md) · [Local order book guide](../guides/local-order-book.md)
- [WebSockets concept](../concepts/websockets.md) · [models](models.md)
