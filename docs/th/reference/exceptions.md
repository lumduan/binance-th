# Exceptions Reference

[หน้าแรก](../index.md) > อ้างอิง > exceptions

[English](../../reference/exceptions.md) · **ไทย**

**โมดูล:** `binance_th.exceptions` · **มีให้ใช้ตั้งแต่:** 1.0.0

error ทุกตัวที่ไลบรารีนี้โยนออกมา จับ `BinanceThError` เพื่อครอบคลุมทั้งหมด หรือจับ subclass เฉพาะตัวเพื่อจัดการเป็นกรณี ๆ ไป

## การ import

```python
from binance_th.exceptions import (
    BinanceThError, BinanceThAPIError, BinanceThRateLimitError, BinanceThServerError,
    BinanceThOrderUnknownError,  # …and the rest below
)
```

## ลำดับชั้น

```text
BinanceThError                     (message, code=None, details=None)
├── BinanceThAPIError              adds status_code, request_id, response_data
│   ├── BinanceThBadRequestError   400
│   ├── BinanceThAuthError         401
│   ├── BinanceThWAFError          403
│   ├── BinanceThIPBannedError     418   adds retry_after
│   ├── BinanceThRateLimitError    429   adds retry_after, used_weight, limit_weight
│   └── BinanceThServerError       5xx   execution status UNKNOWN — not failure
├── BinanceThNetworkError
├── BinanceThTimeoutError          adds timeout
├── BinanceThValidationError       adds field, value  (client-side, pre-send)
├── BinanceThWebSocketError
└── BinanceThOrderUnknownError     adds client_order_id, symbol, resubmittable
```

## แอตทริบิวต์

`BinanceThError` (base): `message: str`, `code: int | None`, `details: dict` โดย `str(err)` จะแสดงผลเป็น
`"[code] message"` เมื่อมีการตั้งค่า code

| Exception | Extra attributes | Raised when |
|-----------|------------------|-------------|
| `BinanceThAPIError` | `status_code`, `request_id`, `response_data` | response ที่ไม่ใช่ 2xx ตัวใดก็ตามที่ตารางด้านล่างยังไม่ได้แยกไว้เฉพาะ |
| `BinanceThBadRequestError` | (มาจาก API error) | `400` — request ผิดรูปแบบ; แก้พารามิเตอร์ก่อนส่งใหม่ |
| `BinanceThAuthError` | (มาจาก API error) | `401` — key, signature หรือ timestamp ผิดหรือขาดหายไป |
| `BinanceThWAFError` | (มาจาก API error) | `403` — ถูก firewall บล็อก; หยุดแล้วตรวจสอบ |
| `BinanceThIPBannedError` | `retry_after` | `418` — IP ถูกแบนอัตโนมัติหลังโดน 429 ซ้ำ ๆ |
| `BinanceThRateLimitError` | `retry_after`, `used_weight`, `limit_weight` | `429` — ถอยรอ `retry_after` วินาที |
| `BinanceThServerError` | (มาจาก API error) | `5xx` — ผลลัพธ์ **UNKNOWN**; ให้กระทบยอด อย่าเพิ่งสรุปว่าล้มเหลว |
| `BinanceThNetworkError` | — | DNS/การเชื่อมต่อ/TLS ล้มเหลว (ชั่วคราว) |
| `BinanceThTimeoutError` | `timeout` | request ใช้เวลาเกิน timeout ที่ตั้งไว้ |
| `BinanceThValidationError` | `field`, `value` | การตรวจสอบฝั่ง client ไม่ผ่านก่อนส่ง |
| `BinanceThWebSocketError` | — | WS เชื่อมต่อ/แปลงข้อมูล/subscribe ล้มเหลว (การเชื่อมต่อใหม่ตามแผนจะไม่โยน error) |
| `BinanceThOrderUnknownError` | `client_order_id`, `symbol`, `resubmittable` | การสร้างออเดอร์เจอ 5xx/timeout/network และการกระทบยอดยืนยันไม่ได้ |

`BinanceThOrderUnknownError.resubmittable` จะเป็น `True` **ก็ต่อเมื่อ** การ query เพื่อกระทบยอดยืนยันได้ชัดเจนว่าออเดอร์
*ไม่ได้* ถูกส่งเข้าไป ถ้าเป็น `False` แปลว่าสถานะไม่รู้จริง ๆ — อย่าส่งซ้ำแบบเดา ๆ

## ตัวช่วย

```python
HTTP_STATUS_MAP: dict[int, type[BinanceThAPIError]]
def get_exception_for_status_code(status_code: int) -> type[BinanceThAPIError]
```
`get_exception_for_status_code` คืนคลาสที่ตรงกับ status code (ค่าใด ๆ ที่ `>= 500` → `BinanceThServerError`;
4xx ที่ไม่รู้จัก → `BinanceThAPIError`)

## ตัวอย่าง

```python
from binance_th.exceptions import BinanceThRateLimitError, BinanceThServerError

try:
    order = await client.orders.create_order(...)
except BinanceThRateLimitError as e:
    await asyncio.sleep(e.retry_after or 1)
except BinanceThServerError:
    order = await client.orders.query_order("BTCTHB", orig_client_order_id=my_id)  # reconcile
```

## ดูเพิ่มเติม

- [Errors & reconciliation](../concepts/errors-and-reconciliation.md) · [Orders guide](../guides/orders.md)
- [Rate limiting](../concepts/rate-limiting.md)
