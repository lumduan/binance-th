# การทดสอบ

[หน้าแรก](../index.md) > การพัฒนา > การทดสอบ

[English](../../development/testing.md) · **ไทย**

## รันชุดทดสอบ

```bash
uv run pytest
```

Coverage ถูกบังคับ: `[tool.pytest.ini_options] addopts` ฮาร์ดโค้ด `--cov-fail-under=90` ไว้ ดังนั้นทั้งชุดทดสอบ
ต้องรักษา coverage ไว้ **≥ 90%** ไม่งั้น pytest จะจบด้วยสถานะไม่เป็นศูนย์

## รันเทสต์เดียว — กับดักเรื่อง coverage

เพราะ coverage วัดจากทั้งแพ็กเกจ การรัน **บางส่วน** จะทำให้ coverage ดูต่ำและ pytest จบด้วยสถานะไม่เป็นศูนย์
**แม้เทสต์ที่เลือกจะผ่าน** ก็ตาม ให้ปิด coverage เมื่อรันแบบเจาะจง:

```bash
uv run pytest tests/test_models/test_orders.py::TestOrderRequest::test_valid_limit_order --no-cov
```

ใช้ `--no-cov` ทุกครั้งที่รันน้อยกว่าทั้งชุด และเอาออก (รันทั้งหมด) ก่อน push

## เทสต์ตรวจอะไรบ้าง

- **Validator ของกฎออเดอร์** ตรวจกับข้อความ `ValueError` เป๊ะ ๆ (LIMIT ⇒ price + timeInForce + quantity;
  MARKET ⇒ quantity **หรือ** quoteOrderQty; STOP\* ⇒ stopPrice; cancel/query ⇒ `orderId` **หรือ**
  `origClientOrderId`) เปลี่ยนข้อความเมื่อไร เทสต์ก็เปลี่ยนตาม
- **การ round-trip ของ alias** — โมเดลรับได้ทั้งชื่อ snake_case และ alias แบบ camelCase บนสาย
- **ตัว parse array** — `Kline.from_list`, `OrderBookEntry.from_list`, `OrderBook.from_api`
- **การแม็ป error** — status code → คลาส exception ที่ถูกต้อง

## Probe และ soak แบบสด (opt-in ไม่อยู่ใน CI)

`scripts/probe_ws.py`, `scripts/probe_userdata.py` และ `scripts/soak_userdata.py` เรียกใช้ API จริงด้วยคีย์จริง —
`soak_userdata.py` สามารถส่งและจัดการ **ออเดอร์จริง** ได้ ทั้งหมดถูกป้องกันและเป็น opt-in อย่าเอาไปต่อกับการรันอัตโนมัติ
พวกมันมีไว้เพื่อยืนยัน[รูปร่างที่ยังไม่ยืนยัน](../concepts/assumed-shapes.md)

## ดูเพิ่มเติม

- [การร่วมพัฒนา](contributing.md) · [ขั้นตอนการออกรุ่น](release-process.md)
