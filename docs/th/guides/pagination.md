# การแบ่งหน้า

[หน้าแรก](../index.md) > คู่มือ > การแบ่งหน้า

[English](../../guides/pagination.md) · **ไทย**

ประวัติบางอย่างยาวเกินกว่าที่หนึ่งคำเรียกจะคืนได้ครบ เมธอดตระกูล `iter_*` จะไล่หน้าให้คุณ แล้วส่งกลับเป็น async stream
เดียวของผลลัพธ์ที่ตัดตัวซ้ำออกแล้ว

## สิ่งที่ควรรู้ก่อน

- [ข้อมูลตลาด](market-data.md) / [การยืนยันตัวตน](../getting-started/authentication.md) (สำหรับประวัติแบบ signed)

---

## Klines ในช่วงเวลายาว

`iter_klines` ไล่หน้าต่างเวลา `[start_time, end_time)` ทีละหน้าขนาด `limit` (ทั้งคู่เป็น epoch มิลลิวินาที):

```python
candles = []
async for k in client.market.iter_klines(
    "BTCTHB", "1h",
    start_time=1700000000000,
    end_time=1700604800000,      # ราว 1 สัปดาห์ถัดมา
    limit=1000,
):
    candles.append(k)
print(len(candles))
```

จะเก็บเป็น list ด้วย comprehension ก็ได้ถ้าถนัดกว่า:

```python
candles = [k async for k in client.market.iter_klines("BTCTHB", "1d",
                                                       start_time=start_ms, end_time=end_ms)]
```

## ประวัติ trade และการฝาก

รูปแบบเดียวกันใช้ได้กับประวัติแบบ signed:

```python
# trade ของคุณบนสัญลักษณ์หนึ่ง
trades = [t async for t in client.account.iter_user_trades(
    "BTCTHB", start_time=start_ms, end_time=end_ms)]

# ประวัติการฝาก
deposits = [d async for d in client.wallet.iter_deposit_history(
    coin="THB", start_time=start_ms, end_time=end_ms)]
```

แต่ละ iterator จะเดินหน้าตาม timestamp/id ของรายการสุดท้าย และตัดตัวซ้ำที่คร่อมขอบหน้า คุณจึงได้ stream ที่สะอาดและเรียงลำดับ

## แบบเรียกครั้งเดียว

เมื่อช่วงข้อมูลพอดีในหนึ่ง response เมธอดที่ไม่ใช่ iterator (`klines`, `user_trades`, `deposit_history`)
จะคืน `list` ธรรมดา — หยิบใช้ตัวพวกนี้เมื่อไม่ต้องไล่หน้า

> หมายเหตุ: ประวัติการถอนเรียกได้ครั้งเดียวเท่านั้น (`withdraw_history`) ไม่มี `iter_withdraw_history`

## ดูเพิ่มเติม

- [คู่มือข้อมูลตลาด](market-data.md)
- [อ้างอิง: market](../reference/market.md) · [account](../reference/account.md) ·
  [wallet](../reference/wallet.md)
