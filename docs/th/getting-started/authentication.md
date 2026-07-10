# การยืนยันตัวตน

[หน้าแรก](../index.md) > เริ่มต้นใช้งาน > การยืนยันตัวตน

[English](../../getting-started/authentication.md) · **ไทย**

ข้อมูลตลาดสาธารณะและ Market Streams ไม่ต้องใช้คีย์ ส่วนการอ่านแบบ signed (บัญชี, กระเป๋าเงิน), การจัดการออเดอร์ และ
user-data stream นั้นต้องใช้ binance-th จะเซ็น (sign) คำขอให้คุณเอง — คุณแค่ใส่คีย์เข้ามา

## ระดับการเข้าถึงสามระดับ

| ระดับ | ต้องใช้ | ใช้โดย |
|-------|---------|---------|
| สาธารณะ | ไม่ต้องใช้อะไร | `client.market.*`, `client.ws.*`, `ping`, `server_time`, `exchange_info` |
| API-key อย่างเดียว | `api_key` | `client.user_stream.*` (listenKey — ไม่ต้องใช้ HMAC secret) |
| Signed (HMAC) | `api_key` + `api_secret` | `client.account.*`, `client.wallet.*`, `client.orders.*` |

## ใส่คีย์

วิธีที่แนะนำคือใช้ไฟล์ `.env` (หรือตัวแปรสภาพแวดล้อม) ที่ `BinanceThConfig` อ่านให้อัตโนมัติ โดยใช้คำนำหน้า
**`BINANCE_TH_`**:

```bash
# .env  (อย่า commit ไฟล์นี้ขึ้น version control)
BINANCE_TH_API_KEY=your_api_key
BINANCE_TH_API_SECRET=your_api_secret
```

```python
from binance_th import BinanceThClient

async with BinanceThClient() as client:      # อ่านจาก .env / env vars
    info = await client.account.account()
```

หรือส่งเข้ามาตรง ๆ:

```python
from binance_th import BinanceThClient, BinanceThConfig

config = BinanceThConfig(api_key="…", api_secret="…")
async with BinanceThClient(config) as client:
    ...
```

`api_secret` ถูกเก็บเป็น `SecretStr` ของ Pydantic จึงไม่ถูกพิมพ์ออกมาใน repr หรือ traceback ตรวจสอบว่าคุณมีคีย์อะไรบ้าง
ด้วย `config.has_credentials()`

## ความลับไม่เคยถูกบันทึกลง log

แม้จะเปิด `log_requests=True` / `log_responses=True` ก็ตาม ค่า signature, `api_secret` และ `listenKey` ใด ๆ
จะถูกกลบ (redact) ก่อนที่จะไปถึง logger เสมอ (แบบเรียกซ้ำ รวมถึง response body ที่ซ้อนอยู่ด้วย) ถึงอย่างนั้นก็
อย่า commit ไฟล์ `.env` จริงเด็ดขาด — เรามีไฟล์ `.env.example` ที่ระบุชื่อตัวแปรที่ถูกต้องให้อยู่แล้ว

## การเซ็น จัดการให้คุณเรียบร้อย

สำหรับ endpoint แบบ signed ไคลเอนต์จะเติม `timestamp` + `recvWindow`, คำนวณ `signature` แบบ HMAC-SHA256 และ
ติดตามค่า offset ของเวลาเซิร์ฟเวอร์ให้ (พร้อมซิงก์ใหม่อัตโนมัติเมื่อเจอ error `-1021` "timestamp outside recvWindow")
คุณไม่ต้องประกอบสิ่งเหล่านี้เองเลย

## ดูเพิ่มเติม

- [ข้อผิดพลาดและการกระทบยอด](../concepts/errors-and-reconciliation.md) — `BinanceThAuthError` และเพื่อน ๆ
- [คู่มือออเดอร์](../guides/orders.md)
- [คู่มือ User-data stream](../guides/user-data-stream.md)
