# ข้อผิดพลาดและการกระทบยอด

[หน้าแรก](../index.md) > แนวคิด > ข้อผิดพลาดและการกระทบยอด

[English](../../concepts/errors-and-reconciliation.md) · **ไทย**

ทุกความล้มเหลวจะยก exception ที่มีชนิดชัดเจน คุณจึงดักเฉพาะกรณีที่สนใจได้ตรง ๆ ทั้งหมดสืบทอดมาจาก `BinanceThError`

## ลำดับชั้น

```text
BinanceThError
├── BinanceThAPIError            (มี status_code, request_id, response_data)
│   ├── BinanceThBadRequestError   400  พารามิเตอร์ผิด — แก้คำขอ
│   ├── BinanceThAuthError         401  คีย์ / signature / นาฬิกาผิด
│   ├── BinanceThWAFError          403  ไฟร์วอลล์บล็อก — หยุดยิงคำขอทันที
│   ├── BinanceThIPBannedError     418  IP ถูกแบนอัตโนมัติหลังโดน 429 ซ้ำ ๆ
│   ├── BinanceThRateLimitError    429  คำขอมากเกินไป (retry_after, used_weight)
│   └── BinanceThServerError       5xx  เซิร์ฟเวอร์ผิดพลาด — ผลลัพธ์ไม่ทราบ (UNKNOWN)
├── BinanceThNetworkError        การเชื่อมต่อ / DNS / TLS ล้มเหลว (มักเป็นชั่วคราว)
├── BinanceThTimeoutError        คำขอเกิน timeout ที่ตั้งไว้
├── BinanceThValidationError     validation ฝั่งไคลเอนต์ล้มเหลว (field, value)
├── BinanceThWebSocketError      WS เชื่อมต่อ / แปลงข้อมูล / subscribe ล้มเหลว
└── BinanceThOrderUnknownError   ส่งออเดอร์ไปแล้ว แต่ยืนยันชะตากรรมของมันไม่ได้
```

```python
from binance_th import BinanceThRateLimitError, BinanceThServerError

try:
    await client.orders.create_order(...)
except BinanceThRateLimitError as e:
    await asyncio.sleep(e.retry_after or 1)
```

## กฎข้อเดียวที่ต้องจำให้ขึ้นใจ: 5xx คือ *ไม่ทราบผล* ไม่ใช่ *ล้มเหลว*

เมื่อคำขอที่เปลี่ยนสถานะ (เช่นการส่งออเดอร์) ได้ `5xx` กลับมา คุณ **ไม่รู้** ว่าตลาดได้ทำรายการนั้นไปแล้วหรือยัง
การเหมาว่า "ล้มเหลว" แล้วส่งซ้ำมั่ว ๆ อาจทำให้ออเดอร์ถูกวางสองครั้ง

ดังนั้น `BinanceThServerError` จึงหมายถึง *ไม่ทราบผล* และสำหรับออเดอร์ ไคลเอนต์จะไปไกลกว่านั้นด้วยการกระทบยอดให้คุณ

## การกระทบยอดออเดอร์ทำงานอย่างไร

`create_order` จะสร้าง client-order-id **ก่อน** ที่จะส่งคำขอออกไป ถ้าการสร้างออเดอร์ไปเจอ `5xx`, timeout หรือ network error
ไคลเอนต์จะสอบถามออเดอร์นั้น **ด้วย id ดังกล่าว**:

- เจอออเดอร์ → คืนค่าราวกับว่าการสร้างสำเร็จ
- เซิร์ฟเวอร์ตอบว่า "unknown order" (`-2013`) → แปลว่ายังไม่ได้ถูกวางแน่นอน →
  `BinanceThOrderUnknownError(resubmittable=True)`
- ตัวการสอบถามกระทบยอดเองล้มเหลว → `BinanceThOrderUnknownError(resubmittable=False)` — ไม่ทราบผลจริง ๆ
  **อย่า** ส่งซ้ำมั่ว ๆ

```python
from binance_th import BinanceThOrderUnknownError

try:
    order = await client.orders.create_order(...)
except BinanceThOrderUnknownError as e:
    if e.resubmittable:
        order = await client.orders.create_order(...)   # ยืนยันแล้วว่ายังไม่ได้วาง — ส่งซ้ำได้ปลอดภัย
    else:
        # ตรวจสถานะของออเดอร์ก่อนทำอะไรต่อ
        ...
```

ไคลเอนต์จะไม่ POST ครั้งที่สองด้วยตัวเอง — การกระทบยอดเป็นแบบสอบถามอย่างเดียว

## ดูเพิ่มเติม

- [คู่มือออเดอร์](../guides/orders.md)
- [การจำกัดอัตราคำขอ](rate-limiting.md) — 429/418 ถูกส่งออกมาอย่างไร
- [อ้างอิง: exceptions](../reference/exceptions.md)
