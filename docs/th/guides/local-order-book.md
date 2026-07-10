# Local Order Book

[หน้าแรก](../index.md) > คู่มือ > Local Order Book

[English](../../guides/local-order-book.md) · **ไทย**

`client.ws.order_book(symbol)` ให้ Order Book ที่ซิงก์ตัวเอง: เริ่มจาก snapshot ทาง REST, เอา depth stream แบบเรียลไทม์
มาใช้ต่อ และ snapshot ใหม่ทันทีถ้าตรวจพบว่าข้อมูลขาดช่วง คุณอ่านค่าจากมันแบบซิงโครนัสในขณะที่มันอัปเดตอยู่เบื้องหลัง

## สิ่งที่ควรรู้ก่อน

- [Market Streams](market-streams.md)
- [WebSocket](../concepts/websockets.md)

---

## เปิด Order Book

```python
async with BinanceThClient() as client:
    order_book = await client.ws.order_book("BTCTHB")
    await order_book.wait_synced()          # บล็อกจนกว่า snapshot แรกจะถูกใช้
    try:
        print("best bid:", order_book.best_bid())   # (price, qty) หรือ None
        print("best ask:", order_book.best_ask())
        print("5 bid บนสุด:", order_book.bids(5))
        print("5 ask บนสุด:", order_book.asks(5))
    finally:
        await order_book.aclose()
```

`order_book(...)` คืน `ManagedOrderBook` ที่เริ่มทำงานแล้ว

## เมธอดสำหรับอ่าน

| เมธอด | คืนค่า |
|--------|--------|
| `book.best_bid()` / `book.best_ask()` | `(Decimal, Decimal)` หรือ `None` |
| `book.bids(n=10)` / `book.asks(n=10)` | top-n `list[(Decimal, Decimal)]` เรียงดีที่สุดก่อน |
| `book.synced` | `bool` — snapshot แรกมาถึงหรือยัง? |
| `await book.wait_synced()` | บล็อกจนกว่าจะซิงก์ |
| `await book.aclose()` | หยุดการซิงก์เบื้องหลัง (เรียกซ้ำได้) |

การอ่านมีต้นทุนต่ำและไม่บล็อก มันคืนสถานะปัจจุบันที่อยู่ในหน่วยความจำ

## วนอ่านเป็นลูป

```python
order_book = await client.ws.order_book("BTCTHB")
await order_book.wait_synced()
for _ in range(10):
    bid, ask = order_book.best_bid(), order_book.best_ask()
    print(bid, ask)
    await asyncio.sleep(1)
await order_book.aclose()
```

## มันคงความถูกต้องได้อย่างไร

เอนจินทำตามอัลกอริทึมมาตรฐาน buffer→snapshot→apply: มันบัฟเฟอร์ depth diff ไว้, ดึง snapshot ทาง REST, ทิ้ง diff
ที่ล้าสมัย, ตรวจว่า diff แรกที่ใช้คร่อม snapshot อยู่ แล้วเอาที่เหลือมาใช้ตามลำดับ (ปริมาณ `0` คือการลบ level นั้นออก)
เมื่อไรที่ update-id ขาดช่วง — รวมถึงหลังเชื่อมต่อใหม่ — มันจะทิ้ง Order Book แล้ว snapshot ใหม่ คุณจึงไม่มีวันอ่าน
Order Book ที่เพี้ยนไปเงียบ ๆ

## ดูเพิ่มเติม

- [คู่มือ Market Streams](market-streams.md) — เหตุการณ์ `watch_depth` ดิบ
- [อ้างอิง: streams](../reference/streams.md) — `ManagedOrderBook`
