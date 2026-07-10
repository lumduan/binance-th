# WalletClient Reference

[หน้าแรก](../index.md) > อ้างอิง > wallet

[English](../../reference/wallet.md) · **ไทย**

**โมดูล:** `binance_th.wallet` · **มีให้ใช้ตั้งแต่:** 1.0.0

การอ่านข้อมูลกระเป๋าเงินแบบ signed (`client.wallet`) — ที่อยู่สำหรับ deposit และประวัติ deposit/withdrawal ทุกเมธอด
เป็นแบบ **signed** namespace นี้เป็นแบบอ่านอย่างเดียว (read-only) ใน 1.0.0 และไม่มีการเคลื่อนย้ายเงิน

> ⚠ **Assumed shapes.** model ของ deposit/withdrawal เป็นไปตาม schema ที่ระบุในเอกสาร แต่ยังไม่ได้ยืนยันครบทุกตัว
> กับ response จริง field ที่ไม่รู้จักจะถูกเก็บไว้ (`extra="allow"`) ดู
> [Assumed shapes](../concepts/assumed-shapes.md)

## การ import

เข้าถึงผ่าน `client.wallet` ต้องใช้ credentials

## เมธอด

### deposit_address

```python
async def deposit_address(coin: str, *, network: str | None = None) -> DepositAddress
```
| พารามิเตอร์ | ชนิด | ค่าเริ่มต้น | คำอธิบาย |
|-----------|------|---------|-------------|
| `coin` | `str` | — | เช่น `"USDT"` |
| `network` | `str \| None` | `None` | chain ที่จะใช้ เมื่อเหรียญนั้นมีหลาย chain |

**Signed (ต้องเซ็น).** **คืนค่า** `DepositAddress` (`.address`, `.coin`, `.tag`, `.url`).

### deposit_history

```python
async def deposit_history(*, coin: str | None = None, start_time: int | None = None,
                          end_time: int | None = None, limit: int | None = None) -> list[DepositRecord]
```
| พารามิเตอร์ | ชนิด | ค่าเริ่มต้น | คำอธิบาย |
|-----------|------|---------|-------------|
| `coin` | `str \| None` | `None` | กรองตามเหรียญ |
| `start_time` / `end_time` | `int \| None` | `None` | epoch ms |
| `limit` | `int \| None` | `None` | จำนวน record สูงสุด |

**Signed (ต้องเซ็น).** **คืนค่า** `list[DepositRecord]` (แบ่งหน้าโดยใช้ค่า integer `insert_time`)

### iter_deposit_history

```python
async def iter_deposit_history(*, coin: str | None = None, start_time: int,
                               end_time: int, limit: int = 1000) -> AsyncIterator[DepositRecord]
```
**Signed (ต้องเซ็น).** Async generator ที่ไล่ดึงประวัติ deposit ทีละหน้าในช่วง `[start_time, end_time)` (**จำเป็น**, epoch
ms) และตัดรายการซ้ำด้วย `tx_id` ใช้งานด้วย `async for` **ให้ค่า (yield)** `DepositRecord`

### withdraw_history

```python
async def withdraw_history(*, coin: str | None = None, start_time: int | None = None,
                           end_time: int | None = None, limit: int | None = None) -> list[WithdrawRecord]
```
**Signed (ต้องเซ็น).** **คืนค่า** `list[WithdrawRecord]` ไม่มี `iter_withdraw_history` ใน 1.0.0 —
เพราะ `WithdrawRecord.apply_time` เป็น string ที่ไม่มี integer timestamp ให้ใช้แบ่งหน้า ดังนั้นถ้าจำเป็นต้องแบ่งหน้าเอง ให้ใช้
`start_time`/`end_time`

## ดูเพิ่มเติม

- [การยืนยันตัวตน](../getting-started/authentication.md) · [account](account.md)
- [models](models.md) · [Assumed shapes](../concepts/assumed-shapes.md)
