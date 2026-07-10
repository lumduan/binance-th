# เอกสาร binance-th

[English](../index.md) · **ไทย**

ไลบรารีไคลเอนต์ Python แบบ async ที่กำหนดชนิด (type) ครบทุกจุด สำหรับ Binance **ประเทศไทย** — ครอบคลุมทั้ง REST และ WebSocket

```python
import asyncio
from binance_th import BinanceThClient

async def main() -> None:
    async with BinanceThClient() as client:
        book = await client.market.depth("BTCTHB", limit=5)
        print(book.bids[0], book.asks[0])

asyncio.run(main())
```

## เส้นทางการเรียนรู้

**เพิ่งเริ่มใช้ binance-th?**

1. [การติดตั้ง](getting-started/installation.md)
2. [เริ่มต้นอย่างรวดเร็ว](getting-started/quickstart.md)
3. [การยืนยันตัวตน](getting-started/authentication.md) — สำหรับการเรียกแบบ signed และ user-data stream
4. เลือกอ่าน[คู่มือ](guides/market-data.md)สักเรื่อง

**คุ้นเคยกับ async Python อยู่แล้ว?** ข้ามไปที่[เอกสารอ้างอิง API](reference/index.md)ได้เลย หรืออ่าน
[`llms.txt`](../../llms.txt) เพื่อดูภาพรวมทั้งหมดในหน้าเดียว

---

## เริ่มต้นใช้งาน 🚀

*ติดตั้งแล้วลองเรียกใช้งานครั้งแรก*

- [การติดตั้ง](getting-started/installation.md) — uv / pip, Python 3.12+
- [เริ่มต้นอย่างรวดเร็ว](getting-started/quickstart.md) — สคริปต์แรกแบบครบวงจร
- [การยืนยันตัวตน](getting-started/authentication.md) — คีย์ ตัวแปรสภาพแวดล้อม และการเรียกไหนที่ต้องใช้

## แนวคิด 💡

*ไม่กี่แนวคิดที่ทำให้ทุกอย่างที่เหลือเข้าใจง่ายขึ้น*

- [GLOBAL กับ SITE](concepts/global-vs-site.md) — การแยกสัญลักษณ์เฉพาะของ Binance ไทย
- [เงินและ Decimal](concepts/money-and-decimals.md) — ทำไมทุกอย่างถึงเป็น `Decimal`
- [ข้อผิดพลาดและการกระทบยอด](concepts/errors-and-reconciliation.md) — ลำดับชั้นของ exception และกฎ "5xx = ไม่ทราบผล"
- [การจำกัดอัตราคำขอ](concepts/rate-limiting.md) — ตัวจำกัดแบบสองหน้าต่างและการปรับตามส่วนหัว
- [WebSocket](concepts/websockets.md) — การเชื่อมต่อ การเชื่อมต่อใหม่ และ keepalive
- [รูปร่างที่ยังไม่ยืนยัน](concepts/assumed-shapes.md) — โมเดลไหนที่ยังไม่ได้ตรวจสอบกับข้อมูลจริง

## คู่มือ 📘

*เน้นการใช้งานจริงตามงาน พร้อมตัวอย่างที่รันได้ครบ*

- [ข้อมูลตลาด](guides/market-data.md) — depth, trades, klines, tickers
- [ออเดอร์](guides/orders.md) — สร้าง / ยกเลิก / สอบถาม พร้อม validation และการกระทบยอดกรณี UNKNOWN
- [Market Streams](guides/market-streams.md) — async iterator ตระกูล `watch_*`
- [Local Order Book](guides/local-order-book.md) — Order Book ที่ซิงก์ตัวเอง
- [User-data stream](guides/user-data-stream.md) — เหตุการณ์ออเดอร์/ยอดเงิน และ order tracker
- [การแบ่งหน้า](guides/pagination.md) — ตัวช่วย `iter_*`

## อ้างอิง API 📖

*ลายเซ็นเมธอดที่แม่นยำ — เป็นสเปก ไม่ใช่บทเรียน*

- [เอกสารอ้างอิง API](reference/index.md) — โครงสร้างแพ็กเกจ ความสามารถ และหน้าแยกตาม namespace

## สถาปัตยกรรม 🏛️

*สร้างขึ้นอย่างไรและทำไม*

- [ภาพรวม](architecture/overview.md) — การแบ่งชั้น (layering)
- [บันทึกการตัดสินใจเชิงสถาปัตยกรรม (ADR)](../plans/adr/README.md) — 17 ADR ที่อยู่เบื้องหลังการออกแบบ

## การพัฒนา 🛠️

*ร่วมพัฒนาหรือออกรุ่น*

- [การร่วมพัฒนา](development/contributing.md)
- [ขั้นตอนการออกรุ่น](development/release-process.md)
- [การทดสอบ](development/testing.md)

## ชุมชน 🌍

- [Changelog](../../CHANGELOG.md) · [นโยบายความปลอดภัย](../../SECURITY.md) ·
  [หลักปฏิบัติของชุมชน](../../CODE_OF_CONDUCT.md)
- ปัญหาและคำถาม: <https://github.com/lumduan/binance-th/issues>
