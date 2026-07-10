# User-data stream

[หน้าแรก](../index.md) > คู่มือ > User-data stream

[English](../../guides/user-data-stream.md) · **ไทย**

`client.user_stream` ส่งกิจกรรมในบัญชีของคุณแบบเรียลไทม์ — อัปเดตออเดอร์, snapshot ยอดเงิน และส่วนต่างของยอดเงิน —
พร้อมมุมมองที่ซ่อมแซมตัวเองของออเดอร์ที่เปิดอยู่

## สิ่งที่ควรรู้ก่อน

- [การยืนยันตัวตน](../getting-started/authentication.md) — ต้องใช้ `api_key` (ไม่ต้องใช้ HMAC secret สำหรับ listenKey)
- [WebSocket](../concepts/websockets.md)

> ⚠ โมเดล **event** ของ user-data เป็น ⚠ASSUMED (ยืนยันการเชื่อมต่อแล้ว แต่ยังไม่ได้จับ event จริงบนบัญชีที่นิ่งอยู่)
> ดู [รูปร่างที่ยังไม่ยืนยัน](../concepts/assumed-shapes.md)

---

## Order tracker (แนะนำ)

วิธีที่ง่ายที่สุดในการตามออเดอร์ของคุณคือ `order_tracker()` — มุมมองแบบเรียลไทม์ที่เริ่มจาก `openOrders`,
อัปเดตจากทุก `executionReport` และอ่านความจริงจาก REST ใหม่ทุกครั้งที่ socket หลุด

```python
async with BinanceThClient() as client:
    tracker = await client.user_stream.order_tracker()
    await tracker.wait_synced()
    print(tracker.open())                 # list[Order] อัปเดตตลอด
    print(tracker.get(12345))             # ออเดอร์เดียวตาม id หรือ None
    ...
    await tracker.aclose()
```

## Event stream ดิบ

ถ้าอยากจัดการ event เอง:

| เมธอด | คืนค่า | เหตุการณ์ |
|--------|--------|-------|
| `client.user_stream.watch_orders()` | `ExecutionReportEvent` | ออเดอร์ถูกสร้าง/fill/ยกเลิก |
| `client.user_stream.watch_account()` | `OutboundAccountPositionEvent` | snapshot ยอดเงินหลังมีการเปลี่ยนแปลง |
| `client.user_stream.watch_balances()` | `BalanceUpdateEvent` | ส่วนต่างจากการฝาก/ถอน/โอน |

```python
async for report in client.user_stream.watch_orders():
    print(report.symbol, report.order_id, report.current_order_status, report.cumulative_filled_qty)
```

Event ของออเดอร์จากสัญลักษณ์ **ทั้ง** GLOBAL และ SITE มาถึงบน iterator เดียวกัน — การแยกถูกจัดการให้คุณแล้ว

## วงจรชีวิต จัดการให้คุณเรียบร้อย

เบื้องหลัง ไคลเอนต์จะสร้าง listenKey — Binance ประเทศไทยคืน **หนึ่งคีย์ต่อชนิดสัญลักษณ์** — คอยต่ออายุด้วย REST `PUT`
เป็นระยะ และลบทิ้งตอนปิด คุณไม่ต้องแตะ listenKey เลย (คีย์ของ SITE ยาวเกินกว่าที่ endpoint keepalive ของตลาดจะรับได้
จึงต่ออายุไม่ได้และซ่อมแซมตัวเองผ่านการเชื่อมต่อใหม่แทน — มองไม่เห็นจากฝั่งคุณอีกเช่นกัน)

การออกจาก `async with` (หรือ `await tracker.aclose()`) จะเก็บกวาดทุกอย่างให้

## ดูเพิ่มเติม

- [คู่มือออเดอร์](orders.md)
- [รูปร่างที่ยังไม่ยืนยัน](../concepts/assumed-shapes.md) — และ `scripts/soak_userdata.py` เพื่อยืนยันรูปร่างของ event
- [อ้างอิง: user-stream](../reference/user-stream.md)
