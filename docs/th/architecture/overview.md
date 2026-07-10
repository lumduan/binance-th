# ภาพรวมสถาปัตยกรรม

[หน้าแรก](../index.md) > สถาปัตยกรรม > ภาพรวม

[English](../../architecture/overview.md) · **ไทย**

binance-th ถูกแบ่งชั้น (layer) อย่างไร และการตัดสินใจออกแบบแต่ละอย่างถูกบันทึกไว้ที่ไหน หน้านี้เป็นแผนที่ —
รายละเอียดเชิงลึกอยู่ใน [HLD](../../plans/hld.md), [FRD](../../plans/frd.md), [WBS](../../plans/wbs.md) และ
[ADR](../../plans/adr/README.md)

## การแบ่งชั้น (Layers)

```text
BinanceThClient                        facade: owns config, transport, and the sub-clients; lifecycle
│
├── MarketClient  AccountClient        REST resource clients — build params, parse typed responses
│   WalletClient  OrdersClient
│        │
│        └── Transport                 one async pipeline for every REST call:
│              signing ─ timesync ─ rate limiter ─ retry ─ envelope unwrap ─ error mapping ─ httpx
│
├── StreamClient                       WebSocket market streams (per-host connections)
│     └── ManagedOrderBook             REST snapshot + depth diff → a self-syncing local book
│
└── UserDataStream                     user-data stream (api-key + listenKey lifecycle)
      └── OrderTracker                 open-orders snapshot + executionReport → a live order view
```

## วงจรชีวิตของคำขอ REST

ทุกคำขอ REST ผ่าน `Transport.request(...)` สำหรับ endpoint แบบ **signed**:

1. Resource client ประกอบพารามิเตอร์เชิงธุรกิจ (ตรวจด้วย `RequestModel` เมื่อมี)
2. ออเดอร์จะทำ[การ validate ก่อนเทรดในเครื่อง](../../plans/adr/ADR-0009-local-pre-trade-validation.md)เพิ่มด้วย
3. Transport เติม `timestamp = now_ms + server_time_offset` แล้วเซ็น query string ที่เรียงแล้วด้วย HMAC-SHA256
   ([signing](../../plans/adr/ADR-0003-request-signing-and-param-ordering.md),
   [time sync](../../plans/adr/ADR-0004-server-time-offset-and-1021-resync.md))
4. [Rate limiter แบบสองหน้าต่าง](../../plans/adr/ADR-0005-dual-window-rate-limiter.md)จองน้ำหนัก (weight) ของคำขอก่อนส่ง
5. `httpx` ส่งคำขอ ความล้มเหลวชั่วคราวจะถูก retry ตาม[อนุกรม backoff](../../plans/adr/ADR-0012-retry-and-backoff-taxonomy.md)
6. [envelope ของ response](../../plans/adr/ADR-0002-response-envelope-unwrap.md) `{code, msg, data}` ถูกแกะเหลือ `data`
   (ยกเว้น endpoint ที่คืนค่าดิบ)
7. response ที่ไม่ใช่ 2xx ถูกแม็ปเป็น[exception ที่มีชนิด](../../plans/adr/ADR-0006-error-taxonomy-and-5xx-unknown-reconciliation.md)
   ส่วน 5xx/timeout ระหว่างสร้างออเดอร์จะทริกเกอร์ **การกระทบยอด** — ดู[ข้อผิดพลาดและการกระทบยอด](../concepts/errors-and-reconciliation.md)
8. payload ถูกแปลงเป็น `ResponseModel` (`extra="allow"`)

ความลับไม่มีวันไปถึง log — ดู[การกลบความลับ](../../plans/adr/ADR-0017-secret-redaction-and-logging.md)

## WebSocket

Market stream ใช้[โทโพโลยีแบบสองโฮสต์](../../plans/adr/ADR-0014-stream-routing-and-base-url-topology.md)
(GLOBAL บน `/gstream`, SITE บน `/nstream`) พร้อมเชื่อมต่อใหม่อัตโนมัติ ส่วน user-data stream ดูแล
[วงจรชีวิตของ listenKey](../../plans/adr/ADR-0008-listenkey-lifecycle-and-manager.md)ด้วยคีย์แยกตามชนิดสัญลักษณ์
ดู [WebSocket](../concepts/websockets.md) และ [GLOBAL กับ SITE](../concepts/global-vs-site.md)

## บันทึกการตัดสินใจ (ADR)

ชุด ADR ทั้งหมดอยู่ใน [`docs/plans/adr/`](../../plans/adr/README.md):

| # | การตัดสินใจ | ระบบย่อย |
|---|----------|-----------|
| [0001](../../plans/adr/ADR-0001-async-core-stack.md) | คอร์ async stack (`httpx` + `websockets`) | transport |
| [0002](../../plans/adr/ADR-0002-response-envelope-unwrap.md) | แกะ envelope ของ response | transport |
| [0003](../../plans/adr/ADR-0003-request-signing-and-param-ordering.md) | การเซ็นคำขอ + การเรียงพารามิเตอร์ | signing |
| [0004](../../plans/adr/ADR-0004-server-time-offset-and-1021-resync.md) | offset เวลาเซิร์ฟเวอร์ + resync เมื่อ `-1021` | time sync |
| [0005](../../plans/adr/ADR-0005-dual-window-rate-limiter.md) | rate limiter แบบสองหน้าต่าง | rate limiting |
| [0006](../../plans/adr/ADR-0006-error-taxonomy-and-5xx-unknown-reconciliation.md) | อนุกรม error + การกระทบยอด 5xx=UNKNOWN | errors |
| [0007](../../plans/adr/ADR-0007-local-order-book-sync.md) | การซิงก์ Order Book ในเครื่อง | order book |
| [0008](../../plans/adr/ADR-0008-listenkey-lifecycle-and-manager.md) | วงจรชีวิต + ตัวจัดการ listenKey | user stream |
| [0009](../../plans/adr/ADR-0009-local-pre-trade-validation.md) | การ validate ก่อนเทรดในเครื่อง | orders |
| [0010](../../plans/adr/ADR-0010-packaging-and-distribution.md) | การแพ็กเกจ + การแจกจ่าย | build/release |
| [0011](../../plans/adr/ADR-0011-global-vs-site-symbol-handling.md) | การจัดการสัญลักษณ์ GLOBAL กับ SITE | symbols |
| [0012](../../plans/adr/ADR-0012-retry-and-backoff-taxonomy.md) | อนุกรม retry + backoff | retry |
| [0013](../../plans/adr/ADR-0013-idempotency-and-client-order-id.md) | idempotency + client order id | orders |
| [0014](../../plans/adr/ADR-0014-stream-routing-and-base-url-topology.md) | การจัดเส้นทาง stream + โทโพโลยี base URL | streams |
| [0015](../../plans/adr/ADR-0015-connection-session-lifecycle-and-pooling.md) | วงจรชีวิต connection/session + pooling | transport |
| [0016](../../plans/adr/ADR-0016-pagination-and-time-window-iteration.md) | การแบ่งหน้า + การไล่หน้าต่างเวลา | pagination |
| [0017](../../plans/adr/ADR-0017-secret-redaction-and-logging.md) | การกลบความลับ + การ log | logging |

## ดูเพิ่มเติม

- [HLD](../../plans/hld.md) · [FRD](../../plans/frd.md) · [WBS](../../plans/wbs.md) · [Roadmap](../../plans/ROADMAP.md)
- [แนวคิด](../concepts/global-vs-site.md) · [อ้างอิง](../reference/index.md)
