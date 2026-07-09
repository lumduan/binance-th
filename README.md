# binance-th

**[English](#english) · [ไทย](#ภาษาไทย)**

A production-ready Python async library for the Binance Thailand API.

---

## English

### Features

- **Type-Safe**: Complete type annotations using Pydantic models
- **Async-First**: All I/O operations use async/await patterns
- **Modern Python**: Supports Python 3.12+
- **Comprehensive Error Handling**: Typed exception hierarchy for precise error handling
- **Rate Limiting**: Built-in rate limiting with automatic backoff (planned)
- **WebSocket Support**: Real-time market data and user streams (planned)

### Installation

```bash
pip install binance-th
```

### Quick Start

```python
from binance_th import BinanceThConfig
from binance_th.models import OrderSide, OrderType

# Create configuration
config = BinanceThConfig(
    api_key="your_api_key",
    api_secret="your_api_secret",
)

# REST client will be available in Phase 2+
```

### Project Status

This library is under active development.

- [x] **Phase 1: Foundation** — Core models, exceptions, configuration
- [ ] **Phase 2: Authentication & Rate Limiting** — HMAC signatures, token bucket
- [ ] **Phase 3: REST API Client** — Full REST API coverage
- [ ] **Phase 4: WebSocket Client** — Market streams, user data streams
- [ ] **Phase 5: Documentation & Release** — Full documentation, PyPI release

### Planning & Architecture Decisions

The full engineering blueprint — high-level design, functional requirements, the milestone→semver
roadmap, and the Architecture Decision Records — lives in [`docs/plans/`](docs/plans/):

- [HLD](docs/plans/hld.md) · [FRD](docs/plans/frd.md) · [WBS](docs/plans/wbs.md) ·
  [ROADMAP](docs/plans/ROADMAP.md)
- [Architecture Decision Records (ADR-0001…0017)](docs/plans/adr/README.md)

### Documentation

See the [API documentation](https://www.binance.th/api-docs/en/?python) for details on the Binance
Thailand API.

### License

MIT

---

## ภาษาไทย

ไลบรารี Python แบบ async ระดับพร้อมใช้งานจริง (production-ready) สำหรับ Binance Thailand API

> โค้ด ชื่อฟังก์ชัน/ตัวแปร และเส้นทาง endpoint ทั้งหมดคงไว้เป็นภาษาอังกฤษตามต้นฉบับ

### คุณสมบัติ

- **ปลอดภัยด้านชนิดข้อมูล (Type-Safe)**: กำกับชนิดข้อมูลครบถ้วนด้วยโมเดล Pydantic
- **Async เป็นหลัก (Async-First)**: การทำงาน I/O ทั้งหมดใช้รูปแบบ async/await
- **Python สมัยใหม่**: รองรับ Python 3.12 ขึ้นไป
- **การจัดการข้อผิดพลาดครบถ้วน**: ลำดับชั้นของ exception ที่มีชนิดชัดเจน เพื่อการจัดการข้อผิดพลาดที่แม่นยำ
- **การจำกัดอัตราการเรียก (Rate Limiting)**: จำกัดอัตราการเรียกอัตโนมัติพร้อม backoff (อยู่ในแผน)
- **รองรับ WebSocket**: ข้อมูลตลาดแบบเรียลไทม์และสตรีมข้อมูลผู้ใช้ (อยู่ในแผน)

### การติดตั้ง

```bash
pip install binance-th
```

### เริ่มต้นใช้งาน

```python
from binance_th import BinanceThConfig
from binance_th.models import OrderSide, OrderType

# สร้างการตั้งค่า (configuration)
config = BinanceThConfig(
    api_key="your_api_key",
    api_secret="your_api_secret",
)

# REST client จะพร้อมใช้งานตั้งแต่ Phase 2 เป็นต้นไป
```

### สถานะโปรเจกต์

ไลบรารีนี้อยู่ระหว่างการพัฒนาอย่างต่อเนื่อง

- [x] **Phase 1: รากฐาน (Foundation)** — โมเดลหลัก, exceptions, การตั้งค่า
- [ ] **Phase 2: การยืนยันตัวตนและการจำกัดอัตรา** — ลายเซ็น HMAC, token bucket
- [ ] **Phase 3: REST API Client** — ครอบคลุม REST API ทั้งหมด
- [ ] **Phase 4: WebSocket Client** — สตรีมข้อมูลตลาดและข้อมูลผู้ใช้
- [ ] **Phase 5: เอกสารและการเผยแพร่** — เอกสารครบถ้วน, เผยแพร่บน PyPI

### การวางแผนและการตัดสินใจเชิงสถาปัตยกรรม

พิมพ์เขียวทางวิศวกรรมทั้งหมด — การออกแบบระดับสูง (HLD), ข้อกำหนดเชิงหน้าที่ (FRD), แผนงานตาม milestone→semver
และบันทึกการตัดสินใจเชิงสถาปัตยกรรม (ADR) — อยู่ในโฟลเดอร์ [`docs/plans/`](docs/plans/):

- [HLD](docs/plans/hld.md) · [FRD](docs/plans/frd.md) · [WBS](docs/plans/wbs.md) ·
  [ROADMAP](docs/plans/ROADMAP.md)
- [บันทึกการตัดสินใจเชิงสถาปัตยกรรม (ADR-0001…0017)](docs/plans/adr/README.md)

### เอกสารประกอบ

ดูรายละเอียด Binance Thailand API ได้ที่ [เอกสาร API](https://www.binance.th/api-docs/en/?python)

### สัญญาอนุญาต

MIT
