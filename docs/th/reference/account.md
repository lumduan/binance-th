# AccountClient Reference

[หน้าแรก](../index.md) > อ้างอิง > account

[English](../../reference/account.md) · **ไทย**

**โมดูล:** `binance_th.account` · **มีให้ใช้ตั้งแต่:** 1.0.0

การอ่านข้อมูลบัญชีแบบ signed (`client.account`) ทุกเมธอดในนี้เป็นแบบ **signed** — ต้องใช้ API key และ
secret โดย client จะเซ็น request แต่ละครั้งให้คุณเอง ทุก field ที่เป็นจำนวนเงินเป็นชนิด `Decimal`

> ⚠ **Assumed shapes.** response model เหล่านี้สร้างขึ้นจาก schema ของ Binance-TH ตามที่ระบุในเอกสาร แต่
> ยังไม่ได้ยืนยันครบทุกตัวกับ response แบบ signed จริง field ที่ไม่รู้จักจะถูกเก็บไว้
> (`extra="allow"`) จึงไม่มีข้อมูลไหนหายไป — แต่ให้ถือว่าชื่อ field ยังเป็นค่าชั่วคราวจนกว่าจะได้รับการยืนยัน ดู
> [Assumed shapes](../concepts/assumed-shapes.md)

## การ import

เข้าถึงผ่าน `client.account` ต้องใช้ credentials — ดูที่ [การยืนยันตัวตน](../getting-started/authentication.md)

## เมธอด

### account

```python
async def account() -> AccountInfo
```
สถานะบัญชีและยอดคงเหลือ **Signed (ต้องเซ็น).** **คืนค่า** `AccountInfo` (`.balances` — แต่ละ `Balance` มี
`.asset`, `.free: Decimal`, `.locked: Decimal`) **อาจยก (raises)** `BinanceThAuthError` หาก credentials
หายไปหรือไม่ถูกต้อง

```python
info = await client.account.account()
for b in info.balances:
    if b.free or b.locked:
        print(b.asset, b.free, b.locked)
```

### trade_fees

```python
async def trade_fees(*, symbol: str | None = None) -> list[TradeFee]
```
| พารามิเตอร์ | ชนิด | ค่าเริ่มต้น | คำอธิบาย |
|-----------|------|---------|-------------|
| `symbol` | `str \| None` | `None` | หนึ่งสัญลักษณ์ หรือทั้งหมดถ้าไม่ระบุ |

**Signed (ต้องเซ็น).** **คืนค่า** `list[TradeFee]` (`.symbol`, `.maker_commission`, `.taker_commission`).

### user_trades

```python
async def user_trades(symbol: str, *, limit: int | None = None,
                      start_time: int | None = None, end_time: int | None = None) -> list[UserTrade]
```
| พารามิเตอร์ | ชนิด | ค่าเริ่มต้น | คำอธิบาย |
|-----------|------|---------|-------------|
| `symbol` | `str` | — | จำเป็น |
| `limit` | `int \| None` | `None` | จำนวน trade สูงสุด |
| `start_time` / `end_time` | `int \| None` | `None` | epoch ms |

**Signed (ต้องเซ็น).** รายการ fill ของคุณเองสำหรับหนึ่งสัญลักษณ์ **คืนค่า** `list[UserTrade]` หากต้องการช่วงข้อมูลทั้งหมด ให้ใช้
[`iter_user_trades`](#iter_user_trades)

### iter_user_trades

```python
async def iter_user_trades(symbol: str, *, start_time: int, end_time: int,
                           limit: int = 1000) -> AsyncIterator[UserTrade]
```
**Signed (ต้องเซ็น).** Async generator ที่ไล่ดึงประวัติ trade ของคุณทีละหน้าในช่วง `[start_time, end_time)`
(**จำเป็น**, epoch ms) และตัดรายการซ้ำด้วย trade id ใช้งานด้วย `async for` **ให้ค่า (yield)** `UserTrade`

```python
fills = [t async for t in client.account.iter_user_trades("BTCTHB")]
```

## ดูเพิ่มเติม

- [การยืนยันตัวตน](../getting-started/authentication.md) · [คู่มือ Pagination](../guides/pagination.md)
- [wallet](wallet.md) · [models](models.md) · [Assumed shapes](../concepts/assumed-shapes.md)
