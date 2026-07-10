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
- **Rate Limiting**: Dual-window token bucket with `x-mbx-used-weight` reconciliation and automatic backoff
- **WebSocket Support**: Real-time market streams (depth, trades, klines, tickers) and a self-syncing local order book; user-data streams planned

### Installation

```bash
pip install binance-th
```

### Quick Start

```python
import asyncio

from binance_th import BinanceThClient, BinanceThConfig


async def main() -> None:
    config = BinanceThConfig(api_key="your_api_key", api_secret="your_api_secret")
    async with BinanceThClient(config) as client:
        # REST: order-book snapshot
        book = await client.market.depth("BTCTHB", limit=5)
        print("top bid/ask:", book.bids[0], book.asks[0])

        # WebSocket: a self-syncing local order book
        order_book = await client.ws.order_book("BTCTHB")
        await order_book.wait_synced()
        print("live best bid/ask:", order_book.best_bid(), order_book.best_ask())
        await order_book.aclose()

        # WebSocket: stream trades (async iterator)
        async for trade in client.ws.watch_trades("BTCTHB"):
            print("trade:", trade.price, trade.quantity)
            break


asyncio.run(main())
```

### Project Status

This library is under active development.

- [x] **Phase 1: Foundation** — Core models, exceptions, configuration
- [x] **Phase 2: Authentication & Rate Limiting** — HMAC signatures, server-time offset, dual-window token bucket
- [x] **Phase 3: REST API Client** — Market, account/wallet reads + orders (create/cancel/query)
- [x] **Phase 4: WebSocket Market Streams** — depth/trade/aggTrade/kline/bookTicker/ticker + self-syncing local order book (live-verified)
- [ ] **Phase 5: User-Data Stream** — listenKey manager, account/order events
- [ ] **Phase 6: Documentation & Release** — Full documentation, PyPI release

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
- **การจำกัดอัตราการเรียก (Rate Limiting)**: token bucket แบบสองหน้าต่าง ปรับตามส่วนหัว `x-mbx-used-weight` พร้อม backoff อัตโนมัติ
- **รองรับ WebSocket**: สตรีมข้อมูลตลาดแบบเรียลไทม์ (depth, trades, klines, tickers) และ local order book ที่ซิงก์ตัวเอง; สตรีมข้อมูลผู้ใช้อยู่ในแผน

### การติดตั้ง

```bash
pip install binance-th
```

### เริ่มต้นใช้งาน

```python
import asyncio

from binance_th import BinanceThClient, BinanceThConfig


async def main() -> None:
    config = BinanceThConfig(api_key="your_api_key", api_secret="your_api_secret")
    async with BinanceThClient(config) as client:
        # REST: order-book snapshot
        book = await client.market.depth("BTCTHB", limit=5)
        print("top bid/ask:", book.bids[0], book.asks[0])

        # WebSocket: a self-syncing local order book
        order_book = await client.ws.order_book("BTCTHB")
        await order_book.wait_synced()
        print("live best bid/ask:", order_book.best_bid(), order_book.best_ask())
        await order_book.aclose()

        # WebSocket: stream trades (async iterator)
        async for trade in client.ws.watch_trades("BTCTHB"):
            print("trade:", trade.price, trade.quantity)
            break


asyncio.run(main())
```

### สถานะโปรเจกต์

ไลบรารีนี้อยู่ระหว่างการพัฒนาอย่างต่อเนื่อง

- [x] **Phase 1: รากฐาน (Foundation)** — โมเดลหลัก, exceptions, การตั้งค่า
- [x] **Phase 2: การยืนยันตัวตนและการจำกัดอัตรา** — ลายเซ็น HMAC, ชดเชยเวลาเซิร์ฟเวอร์, token bucket แบบสองหน้าต่าง
- [x] **Phase 3: REST API Client** — market, account/wallet reads + orders (create/cancel/query)
- [x] **Phase 4: WebSocket Market Streams** — depth/trade/aggTrade/kline/bookTicker/ticker + local order book ที่ซิงก์ตัวเอง (ตรวจสอบกับ feed จริงแล้ว)
- [ ] **Phase 5: User-Data Stream** — ตัวจัดการ listenKey, เหตุการณ์บัญชี/คำสั่ง
- [ ] **Phase 6: เอกสารและการเผยแพร่** — เอกสารครบถ้วน, เผยแพร่บน PyPI

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
