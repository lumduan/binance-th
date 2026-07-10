# BinanceThConfig Reference

[หน้าแรก](../index.md) > อ้างอิง > config

[English](../../reference/config.md) · **ไทย**

**โมดูล:** `binance_th.config` · **มีให้ใช้ตั้งแต่:** 1.0.0

การตั้งค่าต่าง ๆ ของ client เป็นโมเดล `pydantic-settings` โดยทุก field จะอ่านค่าจากตัวแปรสภาพแวดล้อมที่ขึ้นต้นด้วย
`BINANCE_TH_` (ไม่สนใจตัวพิมพ์เล็ก-ใหญ่) หรือจากไฟล์ `.env` และจะส่งค่าเข้าไปตรง ๆ ก็ได้ ส่วนตัวแปรสภาพแวดล้อมที่ไม่รู้จักจะถูกข้ามไป

## การ import

```python
from binance_th import BinanceThConfig
```

```python
config = BinanceThConfig()                       # from env / .env
config = BinanceThConfig(api_key="…", api_secret="…")   # or explicit
```

## ฟิลด์

ตัวแปรสภาพแวดล้อมของแต่ละ field คือ `BINANCE_TH_` ต่อด้วยชื่อ field แบบตัวพิมพ์ใหญ่ (เช่น `api_key` → `BINANCE_TH_API_KEY`)

| Field | Env var | Type | Default | Notes |
|-------|---------|------|---------|-------|
| `api_key` | `BINANCE_TH_API_KEY` | `str \| None` | `None` | จำเป็นสำหรับ endpoint แบบ signed และ user-data |
| `api_secret` | `BINANCE_TH_API_SECRET` | `SecretStr \| None` | `None` | เก็บเป็น `SecretStr` อ่านค่าผ่าน `get_secret_value()` |
| `rest_base_url` | `BINANCE_TH_REST_BASE_URL` | `str` | `https://api.binance.th` | โฮสต์ของ REST |
| `ws_base_url` | `BINANCE_TH_WS_BASE_URL` | `str` | `wss://nbstream.binance.th/w3w/wsa/stream` | stream แบบ single-host ที่สำรองไว้ ตอบ ACK แต่ไม่ส่งข้อมูลตลาดมาให้ — **ไม่ใช่** ค่าเริ่มต้นของ market-stream เก็บไว้เผื่อความเข้ากันได้ในอนาคต / user-data |
| `ws_base_url_global` | `BINANCE_TH_WS_BASE_URL_GLOBAL` | `str` | `wss://www.binance.th/gstream` | เส้นทาง market-stream ของ GLOBAL ที่ยืนยันแล้ว |
| `ws_base_url_site` | `BINANCE_TH_WS_BASE_URL_SITE` | `str` | `wss://www.binance.th/nstream` | เส้นทาง market-stream ของ SITE ที่ยืนยันแล้ว |
| `timeout` | `BINANCE_TH_TIMEOUT` | `float` | `30.0` | timeout ของ request (วินาที); `> 0` |
| `max_retries` | `BINANCE_TH_MAX_RETRIES` | `int` | `3` | จำนวนครั้งที่ลองใหม่เมื่อเจอ error ชั่วคราว; `≥ 0` |
| `enable_rate_limiting` | `BINANCE_TH_ENABLE_RATE_LIMITING` | `bool` | `True` | จำกัดอัตราอัตโนมัติตาม weight |
| `recv_window` | `BINANCE_TH_RECV_WINDOW` | `int` | `5000` | ช่วงเวลาที่ signed request ยังใช้ได้ (มิลลิวินาที); `> 0`, `≤ 60000` |
| `ws_auto_reconnect` | `BINANCE_TH_WS_AUTO_RECONNECT` | `bool` | `True` | เชื่อมต่อ stream ที่หลุดใหม่อัตโนมัติ |
| `ws_ping_interval` | `BINANCE_TH_WS_PING_INTERVAL` | `int` | `20` | ช่วงเวลา ping ของ WS (วินาที); `> 0` |
| `ws_ping_timeout` | `BINANCE_TH_WS_PING_TIMEOUT` | `int` | `10` | timeout ของ ping WS (วินาที); `> 0` |
| `ws_supports_live_subscribe` | `BINANCE_TH_WS_SUPPORTS_LIVE_SUBSCRIBE` | `bool` | `True` | ถ้าเป็น `False` การ (un)subscribe แบบไดนามิกจะเชื่อมต่อใหม่ด้วย URL `?streams=` อันใหม่ |
| `user_stream_keepalive_interval` | `BINANCE_TH_USER_STREAM_KEEPALIVE_INTERVAL` | `float` | `1200.0` | ช่วงเวลา keepalive ของ listenKey (วินาที); `> 0`, `< 1800` (ต่ำกว่าเวลาหมดอายุ 30 นาที) |
| `log_level` | `BINANCE_TH_LOG_LEVEL` | `str` | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR`. |
| `log_requests` | `BINANCE_TH_LOG_REQUESTS` | `bool` | `False` | บันทึก log ของ request ที่ส่งออก (debug) |
| `log_responses` | `BINANCE_TH_LOG_RESPONSES` | `bool` | `False` | บันทึก log ของ response (debug) |

## เมธอด

### has_credentials

```python
def has_credentials() -> bool
```
คืนค่า `True` เมื่อมีทั้ง `api_key` และ `api_secret` ครบทั้งคู่ ใช้แยกเส้นทางระหว่างงานแบบสาธารณะอย่างเดียวกับงานแบบ signed

### get_secret_value

```python
def get_secret_value() -> str | None
```
ค่า API secret แบบข้อความธรรมดา หรือ `None` ถ้ายังไม่ได้ตั้งค่า นี่เป็นที่เดียวที่ secret ถูกแกะออกมา — อย่านำผลลัพธ์ไปเขียน log เด็ดขาด

## ดูเพิ่มเติม

- [Authentication](../getting-started/authentication.md) · [GLOBAL vs SITE](../concepts/global-vs-site.md)
- [Rate limiting](../concepts/rate-limiting.md) · [WebSockets](../concepts/websockets.md)
