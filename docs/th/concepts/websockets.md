# WebSocket

[หน้าแรก](../index.md) > แนวคิด > WebSocket

[English](../../concepts/websockets.md) · **ไทย**

ทั้ง `client.ws` (market stream) และ `client.user_stream` (user data) ทำงานบน WebSocket ไลบรารีจัดการวงจรชีวิต
ของการเชื่อมต่อ การจัดเส้นทาง การเชื่อมต่อใหม่ และ keepalive ให้ คุณจึงแค่วนอ่าน event ได้เลย

## หนึ่งการเชื่อมต่อต่อโฮสต์ เปิดแบบ lazy

ไคลเอนต์จะเปิด WebSocket ก็ต่อเมื่อคุณ subscribe ครั้งแรก แล้วรวมหลาย stream ไว้บนการเชื่อมต่อเดียว เพราะสัญลักษณ์
GLOBAL และ SITE อยู่คนละโฮสต์ (ดู [GLOBAL กับ SITE](global-vs-site.md)) การดูทั้งสองชนิดจะเปิดคนละหนึ่งการเชื่อมต่อ —
แยกตามโฮสต์ โดยที่คุณมองไม่เห็น

## การเชื่อมต่อใหม่เป็นอัตโนมัติ

ถ้า socket หลุด ตัว supervisor จะเชื่อมต่อใหม่ด้วย exponential backoff ที่มีเพดาน แล้ว subscribe stream ของคุณกลับมา
มันยังเชื่อมต่อใหม่ **เชิงรุก** ก่อนถึงเพดานอายุการเชื่อมต่อ ~24 ชั่วโมงของตลาด — เป็นการเชื่อมต่อใหม่ตามแผน ไม่ใช่ error
ระหว่างช่วงขาด Order Book ในเครื่องจะ snapshot ตัวเองใหม่ คุณจึงไม่มีวันเห็นข้อมูลเก่าค้างเงียบ ๆ

ปิดได้ด้วย `BinanceThConfig(ws_auto_reconnect=False)` — จากนั้นการหลุดจะโผล่มาเป็น `BinanceThWebSocketError` บน stream

## Keepalive

สำหรับ market stream นั้น keepalive คือ ping ของ WebSocket ที่ไลบรารี `websockets` จัดการ (`ws_ping_interval` /
`ws_ping_timeout`) ส่วน user-data stream มี keepalive แยกอีกตัว: `listenKey` ต้องถูกต่ออายุด้วย REST `PUT`
ให้ต่ำกว่า 30 นาทีพอสมควร ซึ่งไคลเอนต์จัดตารางให้คุณ (`user_stream_keepalive_interval` ค่าเริ่มต้น 1200 วินาที)

## Backpressure

แต่ละ subscription มีคิวที่มีขอบเขตพร้อมนโยบายทิ้งของเก่าสุด ผู้บริโภคที่ช้าตัวเดียวจึงไม่มีวันทำให้ตัวอ่านที่ใช้ร่วมกัน
ค้างสำหรับ stream อื่น ถ้าคุณตามไม่ทัน คุณจะทิ้ง event เก่าสุด ไม่ใช่ตัวใหม่สุด

## ปิดอย่างสะอาด

การออกจาก `async with BinanceThClient()` (หรือเรียก `client.aclose()`) จะยกเลิก task เบื้องหลัง ปิด socket และ —
สำหรับ user-data stream — ลบ `listenKey` ทิ้ง ส่วนอ็อบเจกต์ที่ WebSocket layer คืนมา (`ManagedOrderBook`, `OrderTracker`)
ก็มี `await aclose()` ของตัวเองถ้าคุณอยากหยุดตัวใดตัวหนึ่งก่อน

## ดูเพิ่มเติม

- [คู่มือ Market Streams](../guides/market-streams.md)
- [คู่มือ Local Order Book](../guides/local-order-book.md)
- [คู่มือ User-data stream](../guides/user-data-stream.md)
