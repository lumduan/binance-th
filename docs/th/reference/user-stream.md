# UserDataStream Reference

[หน้าแรก](../index.md) > อ้างอิง > user-stream

[English](../../reference/user-stream.md) · **ไทย**

**โมดูล:** `binance_th.user_stream` · **มีให้ใช้ตั้งแต่:** 1.0.0

user-data stream (`client.user_stream`) — อัปเดตออเดอร์ บัญชี และยอดคงเหลือของบัญชีคุณแบบเรียลไทม์
ยืนยันตัวตนด้วย **API key** ของคุณ (listenKey จะถูกสร้างและ keep alive ให้อัตโนมัติ); ไม่ได้ใช้การเซ็น
request แบบ signing Binance-TH ออก **listenKey แยกตาม symbol type** (GLOBAL กับ SITE) ซึ่ง
client นี้จัดการให้อย่างโปร่งใส

> ⚠ **Assumed shapes.** โมเดล event ของ user-data ทำตาม schema ในเอกสาร แต่ยังไม่ได้ยืนยันครบทุกตัว
> กับ event จริง; field ที่ไม่รู้จักจะถูกเก็บไว้ (`extra="allow"`) ตรวจสอบด้วย
> [`scripts/soak_userdata.py`](../concepts/assumed-shapes.md) ก่อนจะพึ่งพา field ใด field หนึ่ง

## การ import

เข้าถึงผ่าน `client.user_stream` ต้องใช้ API key ([การยืนยันตัวตน](../getting-started/authentication.md))

## เมธอด

ทุก `watch_*` เป็น async generator — วนด้วย `async for`; อย่า `await` ตัวการเรียกเอง

### watch_orders

```python
async def watch_orders() -> AsyncIterator[ExecutionReportEvent]
```
event แบบ execution-report ที่เกิดขึ้นเมื่อออเดอร์ของคุณเปลี่ยนแปลง (`e=executionReport`)

```python
async with BinanceThClient() as client:
    async for evt in client.user_stream.watch_orders():
        print(evt.symbol, evt.current_order_status)
        break
```

### watch_account

```python
async def watch_account() -> AsyncIterator[OutboundAccountPositionEvent]
```
event แบบ snapshot ยอดคงเหลือของบัญชี (`e=outboundAccountPosition`)

### watch_balances

```python
async def watch_balances() -> AsyncIterator[BalanceUpdateEvent]
```
event ที่เป็น balance-delta ทีละรายการ (`e=balanceUpdate`)

### open_orders_snapshot

```python
async def open_orders_snapshot() -> list[Order]
```
REST snapshot แบบครั้งเดียวของออเดอร์ที่เปิดอยู่ตอนนี้ — เป็นจุดเริ่มต้นที่ [`OrderTracker`](#ordertracker)
ใช้ seed **คืนค่า** `list[Order]`

### order_tracker

```python
async def order_tracker() -> OrderTracker
```
**ต้อง await ก่อน** คืน [`OrderTracker`](#ordertracker) — มุมมองแบบเรียลไทม์ของออเดอร์ที่เปิดอยู่ของคุณ ดูแลให้ทันสมัยจาก
snapshot บวกกับ stream ของออเดอร์ ยังไม่เริ่มทำงาน; ให้เรียก `start()`

### aclose

```python
async def aclose() -> None
```
หยุด stream และปล่อยให้ listenKey หมดอายุ `client.aclose()` จะเรียกให้คุณเอง

---

## OrderTracker

**มีให้ใช้ตั้งแต่:** 1.0.0. แผนที่แบบเรียลไทม์ของออเดอร์ที่เปิดอยู่ของคุณ seed จาก `open_orders_snapshot()` แล้วคอยอัปเดต
ให้ทันสมัยจาก `watch_orders()`

### start

```python
async def start() -> None
```
seed snapshot แล้วเริ่ม consume event ของออเดอร์ เรียกครั้งเดียว

### synced

```python
synced: bool  # property
```
เป็น `True` เมื่อ snapshot และ stream ถูกกระทบยอดตรงกันแล้ว

### wait_synced

```python
async def wait_synced() -> None
```
await จนกว่า `synced` จะเป็น `True`

### open

```python
def open() -> list[Order]
```
ออเดอร์ที่เปิดอยู่ในปัจจุบัน

### get

```python
def get(order_id: int) -> Order | None
```
ออเดอร์ที่ติดตามอยู่หนึ่งตัวตาม id หรือ `None`

### aclose

```python
async def aclose() -> None
```
หยุดติดตาม

```python
tracker = await client.user_stream.order_tracker()
await tracker.start()
await tracker.wait_synced()
print([o.order_id for o in tracker.open()])
await tracker.aclose()
```

## ดูเพิ่มเติม

- [คู่มือ user-data stream](../guides/user-data-stream.md) · [orders](orders.md)
- [Assumed shapes](../concepts/assumed-shapes.md) · [GLOBAL vs SITE](../concepts/global-vs-site.md)
