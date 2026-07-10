# API Reference

[หน้าแรก](../index.md) > อ้างอิง

[English](../../reference/index.md) · **ไทย**

**มีให้ใช้ตั้งแต่:** 1.0.0 — signature ที่เป๊ะ, พารามิเตอร์ และชนิดของค่าที่คืนของทุกเมธอด สำหรับเนื้อหาแบบเล่าเรื่อง
ดูที่ [คู่มือ](../guides/market-data.md); ถ้าอยากได้ทั้งหมดในหน้าเดียว ดู [`llms.txt`](../../../llms.txt)

## โครงสร้างแพ็กเกจ

```text
binance_th
├── BinanceThClient                → the async entry point       → reference/client.md
│   ├── .market   → MarketClient    → public market data         → reference/market.md
│   ├── .account  → AccountClient   → signed account reads        → reference/account.md
│   ├── .wallet   → WalletClient    → signed wallet reads         → reference/wallet.md
│   ├── .orders   → OrdersClient    → signed order management     → reference/orders.md
│   ├── .ws       → StreamClient    → WebSocket market streams    → reference/streams.md
│   └── .user_stream → UserDataStream → user-data stream          → reference/user-stream.md
├── BinanceThConfig                 → settings                    → reference/config.md
├── binance_th.exceptions           → error hierarchy             → reference/exceptions.md
└── binance_th.models               → Pydantic models + enums     → reference/models.md
```

## Namespace

| หน้า | คลาส | Auth | เมธอด |
|------|-------|------|---------|
| [client](client.md) | `BinanceThClient` | สาธารณะ | `ping`, `server_time`, `exchange_info`, `symbol_types`, `aclose` |
| [market](market.md) | `MarketClient` | สาธารณะ | `depth`, `trades`, `agg_trades`, `klines`, `iter_klines`, `ticker_price`, `ticker_24hr`, `book_ticker`, `reference_price`, `execution_rules` |
| [account](account.md) | `AccountClient` | signed | `account`, `trade_fees`, `user_trades`, `iter_user_trades` |
| [wallet](wallet.md) | `WalletClient` | signed | `deposit_address`, `deposit_history`, `iter_deposit_history`, `withdraw_history` |
| [orders](orders.md) | `OrdersClient` | signed | `create_order`, `cancel_order`, `query_order`, `open_orders` |
| [streams](streams.md) | `StreamClient`, `ManagedOrderBook` | สาธารณะ | `watch_depth/trades/agg_trades/klines/book_ticker/ticker`, `order_book` |
| [user-stream](user-stream.md) | `UserDataStream`, `OrderTracker` | api-key | `watch_orders/account/balances`, `order_tracker` |
| [config](config.md) | `BinanceThConfig` | — | การตั้งค่าทั้งหมด + env vars |
| [exceptions](exceptions.md) | `BinanceThError` … | — | ลำดับชั้นของ exception |
| [models](models.md) | โมเดล Pydantic + enum | — | โมเดลที่ export, ชุดค่าของ enum, `from_list`/`from_api` |

## นำทางด่วน: ต้องใช้หน้าไหน?

| ฉันอยาก… | ไปที่ |
|-----------|-------|
| อ่าน Order Book (ครั้งเดียว / เรียลไทม์) | [market](market.md) `depth` / [streams](streams.md) `order_book` |
| สตรีม trade, แท่งเทียน, ticker | [streams](streams.md) |
| สร้าง / ยกเลิก / เรียกดูออเดอร์ | [orders](orders.md) |
| อ่านยอดคงเหลือหรือประวัติการเทรด | [account](account.md) |
| ที่อยู่สำหรับฝาก / ประวัติการฝาก | [wallet](wallet.md) |
| ติดตามออเดอร์ของฉันแบบเรียลไทม์ | [user-stream](user-stream.md) |
| ตั้งค่าคีย์ / URL / ลิมิต | [config](config.md) |
| จัดการ error | [exceptions](exceptions.md) |
| ดู field ของโมเดล หรือค่าต่าง ๆ ของ enum | [models](models.md) |

## ดูเพิ่มเติม

- [หน้าแรกของเอกสาร](../index.md)
- [`llms.txt`](../../../llms.txt) — ทั้งหมดในที่เดียว ย่อมาให้ AI agent อ่าน
