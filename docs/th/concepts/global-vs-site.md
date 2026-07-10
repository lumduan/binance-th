# สัญลักษณ์ GLOBAL กับ SITE

[หน้าแรก](../index.md) > แนวคิด > GLOBAL กับ SITE

[English](../../concepts/global-vs-site.md) · **ไทย**

Binance ประเทศไทยมีสัญลักษณ์การเทรดสองแบบ และการรู้ว่าอันไหนเป็นแบบไหนจะช่วยอธิบายหลายอย่างที่ไม่งั้นจะดูไม่สอดคล้องกัน

- **GLOBAL** — ใช้ร่วมกับแพลตฟอร์ม Binance หลัก (เช่น `BTCUSDT`)
- **SITE** — เฉพาะภูมิภาคไทย (เช่น `BTCTHB`)

ทั้งสองแบบเปิดออกมาเป็น enum `SymbolType` (`SymbolType.GLOBAL` / `SymbolType.SITE`)

## ทำไมถึงสำคัญ

**ทั้งสองไม่ได้มีฟิลด์เหมือนกันเสมอไป** Binance ไทยไม่รับประกันความเท่าเทียม (parity) ระหว่างสองแบบ ดังนั้นบางฟิลด์ในโมเดล
จึงเป็น `Optional` เพียงเพราะมันปรากฏเฉพาะบางแบบเท่านั้น — ตัวอย่างเช่น `depthUpdate` จากสัญลักษณ์ SITE จะมี `T`/`pu`
ที่ของ GLOBAL ไม่มี, `trade`/`aggTrade` จาก GLOBAL จะมีธง `M` ที่ของ SITE ไม่มี, และหลายฟิลด์ใน `Ticker24hr` กับ `Trade`
จะเป็น `null` บนสัญลักษณ์ SITE

**stream WebSocket ของทั้งสองอยู่คนละโฮสต์** stream GLOBAL มาจาก `ws_base_url_global` (`/gstream`) ส่วน SITE มาจาก
`ws_base_url_site` (`/nstream`) ไลบรารีจะหาชนิดของสัญลักษณ์และจัดเส้นทางการเชื่อมต่อให้เอง — คุณแค่ส่งสัญลักษณ์เข้าไป
การดูสัญลักษณ์ GLOBAL หนึ่งตัวและ SITE หนึ่งตัวก็แค่เปิดสองการเชื่อมต่ออยู่เบื้องหลัง

**บาง endpoint มีเฉพาะ GLOBAL** `client.market.reference_price(...)` และ `client.market.execution_rules()`
มีเฉพาะสำหรับสัญลักษณ์ GLOBAL เท่านั้น การเรียกด้วยสัญลักษณ์ SITE/THB จะได้ `400` (`BinanceThBadRequestError`)

## ตรวจชนิดของสัญลักษณ์

```python
async with BinanceThClient() as client:
    types = await client.symbol_types(symbol="BTCTHB")
    print(types[0].symbol, types[0].symbol_type)   # BTCTHB SymbolType.SITE
```

`client.symbol_types()` (ไม่ใส่อาร์กิวเมนต์) จะคืนรายการทั้งหมด

## User-data stream

User-data stream ก็ถูกแยกเช่นกัน: `POST /api/v1/listenKey` คืน **หนึ่งคีย์ต่อหนึ่งชนิด** (พฤติกรรมเฉพาะของไทย)
ดังนั้นไคลเอนต์จึงดูแลหนึ่งการเชื่อมต่อต่อชนิดไว้เบื้องหลัง คุณไม่ต้องจัดการเอง — `client.user_stream.*` จะรวมเหตุการณ์
จากทั้งสองให้ ดู[คู่มือ user-data stream](../guides/user-data-stream.md)

## ดูเพิ่มเติม

- [WebSocket](websockets.md) — การเชื่อมต่อและการจัดเส้นทางทำงานอย่างไร
- [รูปร่างที่ยังไม่ยืนยัน](assumed-shapes.md) — ทำไมบางฟิลด์จึงยังเป็นการชั่วคราว
- [คู่มือข้อมูลตลาด](../guides/market-data.md)
