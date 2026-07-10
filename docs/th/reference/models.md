# Models Reference

[หน้าแรก](../index.md) > อ้างอิง > models

[English](../../reference/models.md) · **ไทย**

**โมดูล:** `binance_th.models` · **มีให้ใช้ตั้งแต่:** 1.0.0

โมเดล Pydantic และ enum สาธารณะทั้งหมด ปกติแล้วคุณแทบไม่ต้องสร้างพวกนี้เอง — client จะคืนค่ามาให้ — แต่การรู้จัก
field และชุดค่าของมันนี่แหละที่ทำให้ typed API มีประโยชน์ขึ้นมา

## การ import

```python
from binance_th.models import Order, OrderBook, Ticker24hr, KlineInterval  # …etc
```

ชื่อโมเดลและ enum ทุกตัวถูก re-export ออกมาจาก root ของแพ็กเกจด้วย (`from binance_th import Order`)

## ข้อตกลง (conventions)

- **Base class สองตัว** response จะ subclass มาจาก `ResponseModel` (`extra="allow"` — field จาก API ที่ไม่รู้จัก
  จะถูกเก็บไว้ ไม่ทิ้ง) ส่วน request จะ subclass มาจาก `RequestModel` (`extra="forbid"` — พิมพ์ผิดจะถูกปฏิเสธก่อนส่ง)
  ทั้งคู่รับได้ทั้งชื่อแบบ snake_case **หรือ** alias แบบ camelCase และตัดช่องว่างหัวท้ายให้อัตโนมัติ
- **`Decimal` สำหรับเรื่องเงิน** ทุกราคา ปริมาณ ยอดคงเหลือ ค่าธรรมเนียม และค่าคอมมิชชัน เป็น `Decimal` เสมอ ไม่เคยใช้
  `float`
- **snake_case ↔ camelCase** โค้ดของคุณใช้ `order_id`; ฝั่งสายส่งใช้ `orderId` โดยตั้ง alias แยกเป็นราย
  field
- **endpoint ที่คืนค่าเป็น array ต้องใช้ classmethod** response บางตัวเป็น array แบบเรียงตามตำแหน่ง ไม่ใช่ JSON object
  จึงต้องสร้างด้วย classmethod ไม่ใช่ `Model(**data)`:

  | Model | Classmethod |
  |-------|-------------|
  | `OrderBookEntry` | `OrderBookEntry.from_list([price, qty])` |
  | `OrderBook` | `OrderBook.from_api(raw_dict)` |
  | `Kline` | `Kline.from_list([...])` |

## โมเดล response

| Group | Models |
|-------|--------|
| พื้นฐาน / meta | `ServerTime`, `ExchangeInfo`, `SymbolInfo`, `SymbolFilter`, `SymbolTypeInfo`, `RateLimit` |
| ตลาด | `OrderBook`, `OrderBookEntry`, `Trade`, `AggregateTrade`, `Kline`, `Ticker24hr`, `PriceTicker`, `BookTicker`, `ReferencePrice`, `ExecutionRules`, `SymbolExecutionRules`, `ExecutionRule` |
| บัญชี / wallet ⚠ | `AccountInfo`, `Balance`, `TradeFee`, `UserTrade`, `DepositAddress`, `DepositRecord`, `WithdrawRecord`, `WithdrawResult`, `SubAccountTransfer`, `ListenKey` |
| ออเดอร์ | `Order` |
| event ของ market-stream | `StreamMessage`, `DepthUpdateEvent`, `TradeEvent`, `AggTradeEvent`, `KlineEvent`, `KlineData`, `BookTickerEvent`, `TickerEvent` |
| event ของ user-data ⚠ | `ExecutionReportEvent`, `OutboundAccountPositionEvent`, `AccountBalanceDelta`, `BalanceUpdateEvent`, `ListenKeyExpiredEvent` |

> ⚠ โมเดล account/wallet และ user-data อ้างอิงตาม schema ของ Binance-TH ตามเอกสาร แต่ยังไม่ได้ยืนยันกับ
> response จริงทั้งหมด `extra="allow"` จะเก็บทุกอย่างที่ยังไม่ได้ทำเป็นโมเดลไว้ให้ ดูเพิ่มที่
> [Assumed shapes](../concepts/assumed-shapes.md) ส่วนรูปแบบ event ของ market-stream ยืนยันกับของจริงแล้ว
> (2026-07-09) โดยบาง field ที่เป็นแบบ GLOBAL-vs-SITE เป็น optional (ไม่มี parity, ADR-0011)

## โมเดล request

subclass มาจาก `RequestModel` (`extra="forbid"`) โดยตั้งใจไม่ใส่ `timestamp`/`signature` — client จะเติมให้เอง
ตอน signing

| Model | Purpose | Validation |
|-------|---------|-----------|
| `OrderRequest` | สร้าง payload สำหรับ `create_order` | LIMIT ⇒ price + timeInForce + quantity; MARKET ⇒ quantity **หรือ** quoteOrderQty; STOP\* ⇒ stopPrice |
| `CancelOrderRequest` | ยกเลิกด้วย id | ต้องมี `order_id` **หรือ** `orig_client_order_id` |
| `QueryOrderRequest` | query ด้วย id | ต้องมี `order_id` **หรือ** `orig_client_order_id` |

## Enum

ทั้งหมดเป็น `StrEnum` (เทียบค่า/serialize เป็นค่า string ของตัวเอง) ยกเว้น `DepositStatus`/`WithdrawStatus`
ที่เป็น enum แบบ `int`

| Enum | Members (value) |
|------|-----------------|
| `OrderSide` | `BUY`, `SELL` |
| `OrderType` | `LIMIT`, `MARKET`, `STOP_LOSS`, `STOP_LOSS_LIMIT`, `TAKE_PROFIT`, `TAKE_PROFIT_LIMIT`, `LIMIT_MAKER` |
| `OrderStatus` | `NEW`, `PARTIALLY_FILLED`, `FILLED`, `CANCELED`, `REJECTED`, `EXPIRED` |
| `TimeInForce` | `GTC`, `IOC`, `FOK` |
| `KlineInterval` | `MINUTE_1`…`MINUTE_30` (`1m,3m,5m,15m,30m`), `HOUR_1`…`HOUR_12` (`1h,2h,4h,6h,8h,12h`), `DAY_1`/`DAY_3` (`1d,3d`), `WEEK_1` (`1w`), `MONTH_1` (`1M`) |
| `SymbolType` | `GLOBAL`, `SITE` |
| `SymbolStatus` | `TRADING`, `HALT`, `BREAK` |
| `RateLimitType` | `REQUEST_WEIGHT`, `ORDERS`, `RAW_REQUESTS` |
| `RateLimitInterval` | `SECOND`, `MINUTE`, `HOUR`, `DAY` |
| `FilterType` | `PRICE_FILTER`, `PERCENT_PRICE`, `LOT_SIZE`, `MIN_NOTIONAL`, `ICEBERG_PARTS`, `MARKET_LOT_SIZE`, `MAX_NUM_ORDERS`, `MAX_NUM_ALGO_ORDERS`, `MAX_NUM_ICEBERG_ORDERS`, `EXCHANGE_MAX_NUM_ORDERS`, `EXCHANGE_MAX_NUM_ALGO_ORDERS` |
| `DepositStatus` (int) | `PENDING=0`, `SUCCESS=1`, `CREDITED=6` |
| `WithdrawStatus` (int) | `EMAIL_SENT=0`, `CANCELLED=1`, `AWAITING_APPROVAL=2`, `REJECTED=3`, `PROCESSING=4`, `FAILURE=5`, `COMPLETED=6` |

## สมาชิกอำนวยความสะดวก

| On | Member | Gives |
|----|--------|-------|
| `ExchangeInfo` | `get_symbol(sym)` | `SymbolInfo \| None` |
| `ExecutionRules` | `get_symbol(sym)` | `SymbolExecutionRules \| None` |
| `AccountInfo` | `get_balance(asset)`, `get_non_zero_balances()` | `Balance \| None`, `list[Balance]` |
| `Balance` | `total` | `free + locked` |
| `Order` | `is_filled`, `is_active`, `filled_percent` | ตัวช่วยเกี่ยวกับสถานะออเดอร์ |
| `binance_th.models` | `order_from_execution_report(evt)` | `Order` ที่สร้างจาก `ExecutionReportEvent` |

## ดูเพิ่มเติม

- [Money & Decimals](../concepts/money-and-decimals.md) · [Assumed shapes](../concepts/assumed-shapes.md)
- [market](market.md) · [orders](orders.md) · [streams](streams.md)
