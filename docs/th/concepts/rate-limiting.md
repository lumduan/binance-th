# การจำกัดอัตราคำขอ (rate limiting)

[หน้าแรก](../index.md) > แนวคิด > การจำกัดอัตราคำขอ

[English](../../concepts/rate-limiting.md) · **ไทย**

binance-th จะคุมจังหวะคำขอของคุณให้อยู่ใต้ลิมิตของ Binance ประเทศไทย และแก้ตัวเองจากตัวนับของตลาดเอง มันเปิดโดยปริยาย
คุณแทบไม่ต้องคิดถึงมันเลย

## สองหน้าต่าง

Binance บังคับงบสองแบบพร้อมกัน — งบ **request-weight** (แต่ละ endpoint มีน้ำหนัก) และงบ **order-count**
ตัว rate limiter จะติดตามทั้งสองหน้าต่างและรอเมื่ออันใดอันหนึ่งจะเกิน แทนที่จะปล่อยให้คุณชน `429`

## กระทบยอดจากส่วนหัวของ response

ทุก response ของ REST จะพก `x-mbx-used-weight-1m` (น้ำหนักที่เซิร์ฟเวอร์นับจริง) ตัว rate limiter อ่านส่วนหัวนั้น
แล้วปรับค่าประมาณของตัวเองให้ตรง จึงแม่นยำอยู่เสมอแม้บางคำขอจะหนักกว่าที่คาด ส่วนตัวลิมิตจริง ๆ นั้นรับมาจาก
`client.exchange_info()` ครั้งแรกที่คุณเรียก

## ถ้าชนลิมิตขึ้นมา

`429` จะยก `BinanceThRateLimitError` พร้อม `retry_after` และ `used_weight` การละเมิดซ้ำ ๆ อาจยกระดับเป็น `418`
(`BinanceThIPBannedError`) พร้อม `retry_after` ที่ยาวกว่า ทั้งคู่บอกคุณว่าต้องรอนานแค่ไหน

```python
from binance_th import BinanceThRateLimitError

try:
    await client.market.depth("BTCTHB")
except BinanceThRateLimitError as e:
    await asyncio.sleep(e.retry_after or 1)
```

## ปิดมัน

```python
from binance_th import BinanceThConfig
config = BinanceThConfig(enable_rate_limiting=False)   # ตอนนี้คุณคุมจังหวะเอง
```

เปิดไว้เถอะ เว้นแต่คุณมีตัว limiter ของตัวเองอยู่ข้างหน้าแล้ว

## ดูเพิ่มเติม

- [ข้อผิดพลาดและการกระทบยอด](errors-and-reconciliation.md)
- [อ้างอิง: config](../reference/config.md)
