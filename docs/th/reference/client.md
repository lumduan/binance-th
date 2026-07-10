# BinanceThClient Reference

[หน้าแรก](../index.md) > อ้างอิง > client

[English](../../reference/client.md) · **ไทย**

**โมดูล:** `binance_th.client` · **มีให้ใช้ตั้งแต่:** 1.0.0

จุดเริ่มต้นแบบ async เป็นเจ้าของการเชื่อมต่อ HTTP + WebSocket และเปิดให้เข้าถึง sub-client ต่าง ๆ ใช้งานมันแบบ
async context manager

## การ import

```python
from binance_th import BinanceThClient, BinanceThConfig
```

## Constructor (ตัวสร้าง)

```python
BinanceThClient(config: BinanceThConfig | None = None, *, transport: Transport | None = None)
```

| พารามิเตอร์ | ชนิด | ค่าเริ่มต้น | คำอธิบาย |
|-----------|------|---------|-------------|
| `config` | `BinanceThConfig \| None` | `None` | การตั้งค่า; ค่าเริ่มต้นคือ `BinanceThConfig()` (อ่านจาก env `BINANCE_TH_*` / `.env`) |
| `transport` | `Transport \| None` | `None` | จุดสำหรับ inject แบบ keyword-only (ไว้ใช้ตอนเทส); ปล่อยว่างไว้ |

```python
async with BinanceThClient() as client:
    ...
```

## แอตทริบิวต์

| แอตทริบิวต์ | ชนิด | คำอธิบาย |
|-----------|------|-------------|
| `client.market` | `MarketClient` | [ข้อมูลตลาดสาธารณะ](market.md) |
| `client.account` | `AccountClient` | [การอ่านข้อมูลบัญชีแบบ signed](account.md) |
| `client.wallet` | `WalletClient` | [การอ่านข้อมูล wallet แบบ signed](wallet.md) |
| `client.orders` | `OrdersClient` | [การจัดการออเดอร์แบบ signed](orders.md) |
| `client.ws` | `StreamClient` | [stream ข้อมูลตลาดผ่าน WebSocket](streams.md) |
| `client.user_stream` | `UserDataStream` | [user-data stream](user-stream.md) |
| `client.is_closed` | `bool` | จะเป็น True เมื่อปิดแล้ว |

## เมธอด

### ping

```python
async def ping() -> bool
```
`GET /api/v1/ping` สาธารณะ คืน `True` ถ้า API ตอบกลับ **คืนค่า** `bool`

### server_time

```python
async def server_time() -> ServerTime
```
`GET /api/v1/time` สาธารณะ; ยังรีเฟรช time-offset ที่ใช้เซ็น request ภายในให้ด้วย **คืนค่า** `ServerTime`

### exchange_info

```python
async def exchange_info(*, force: bool = False) -> ExchangeInfo
```
`GET /api/v1/exchangeInfo` แคชไว้หลังเรียกครั้งแรก; และยังตั้งค่าเริ่มต้นให้ rate limiter ด้วย ส่ง `force=True`
เพื่อดึงใหม่ **คืนค่า** `ExchangeInfo` (ใช้ `.get_symbol(sym)` เพื่อเอา `SymbolInfo`)

### symbol_types

```python
async def symbol_types(*, symbol: str | None = None) -> list[SymbolTypeInfo]
```
`GET /api/v1/symbolType` สาธารณะ บอกชนิด GLOBAL/SITE ของแต่ละสัญลักษณ์; เป็น list เสมอ ส่ง `symbol=` เพื่อกรอง
**คืนค่า** `list[SymbolTypeInfo]`

### aclose

```python
async def aclose() -> None
```
ปิด market stream ก่อน แล้วตามด้วย user-data stream แล้วจึงปิด transport ทำงานซ้ำได้ (idempotent) ถูกเรียกอัตโนมัติ
เมื่อออกจาก `async with`

## ดูเพิ่มเติม

- [เริ่มต้นอย่างรวดเร็ว](../getting-started/quickstart.md)
- [config](config.md) · [exceptions](exceptions.md)
