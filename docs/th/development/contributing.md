# การร่วมพัฒนา

[หน้าแรก](../index.md) > การพัฒนา > การร่วมพัฒนา

[English](../../development/contributing.md) · **ไทย**

คู่มือฉบับเต็มอยู่ที่ [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) หน้านี้เป็นฉบับย่อสำหรับการลงมือทำในโค้ด
ส่วนนโยบายความปลอดภัยอยู่ใน [`SECURITY.md`](../../../SECURITY.md)

## ตั้งค่า

โปรเจกต์นี้ใช้ [`uv`](https://docs.astral.sh/uv/) (ไม่ใช่ pip/poetry) และต้องใช้ Python **3.12+** (CI รัน 3.13 ด้วย)

```bash
uv sync --extra dev        # dependency ตอนรันไทม์ + สำหรับ dev
```

## ด่านคุณภาพ (quality gate)

CI รันสามงานอิสระ — **lint**, **type-check**, **test** — และทั้งหมดต้องผ่าน รันในเครื่องก่อน push:

```bash
uv run ruff format .        # จัดรูปแบบ  (เช็คอย่างเดียว: ruff format --check .)
uv run ruff check . --fix   # lint + แก้อัตโนมัติ
uv run mypy binance_th      # type-check แบบ strict
uv run pytest               # ทดสอบ บังคับ coverage ≥90%
uv run pre-commit run --all-files   # ทุกอย่าง รวม hook สุขอนามัย
```

`mypy` เป็น `strict = true` ส่วน `ruff` ตั้งความยาวบรรทัดไว้ 100 พร้อมชุดกฎกว้าง (รวม `ASYNC`)

## ข้อตกลงที่พลาดได้ง่าย

- **ใช้ `Decimal` กับเงิน** — ห้ามใช้ `float` ดู[เงินและ Decimal](../concepts/money-and-decimals.md)
- **เลือก base model ให้ถูก** — response สืบทอด `ResponseModel` (`extra="allow"`) ส่วน request สืบทอด
  `RequestModel` (`extra="forbid"`) ดู[models](../reference/models.md)
- **endpoint แบบ array** ต้องมี classmethod `from_list`/`from_api`
- **สัญลักษณ์สาธารณะ** ต้องอยู่ใน `__all__` ของโมดูล และถูก re-export จากรากของแพ็กเกจ
- **GLOBAL กับ SITE** เป็นการแยกจริง — รักษาไว้ในโค้ด stream/สัญลักษณ์ ([แนวคิด](../concepts/global-vs-site.md))

## Commit

ใช้ Conventional Commits พร้อม scope ตามเฟส เช่น `feat(phase-01): …`, `fix(ci): …`, `docs: …`

## ดูเพิ่มเติม

- [การทดสอบ](testing.md) · [ขั้นตอนการออกรุ่น](release-process.md)
- [ภาพรวมสถาปัตยกรรม](../architecture/overview.md)
