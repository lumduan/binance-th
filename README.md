# binance-th

**[English](#english) · [ไทย](#ภาษาไทย)**

[![CI](https://github.com/lumduan/binance-th/actions/workflows/ci.yml/badge.svg)](https://github.com/lumduan/binance-th/actions/workflows/ci.yml)
[![Security](https://github.com/lumduan/binance-th/actions/workflows/security.yml/badge.svg)](https://github.com/lumduan/binance-th/actions/workflows/security.yml)
[![PyPI](https://img.shields.io/pypi/v/binance-th.svg)](https://pypi.org/project/binance-th/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/binance-th.svg)](https://pypi.org/project/binance-th/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Async/Await](https://img.shields.io/badge/async-await-green.svg)](https://docs.python.org/3/library/asyncio.html)
[![Typed](https://img.shields.io/badge/typed-pydantic-red.svg)](https://pydantic.dev/)

binance-th — an async Python client for the **Binance Thailand** API, REST and WebSocket, fully typed.

Talk to the exchange with plain `async`/`await`: place orders, read market data, and follow live
depth, trades, and your own account over WebSocket — every payload a typed Pydantic model, every price
a `Decimal`. Built for trading tools, data pipelines, and AI agents.

---

## English

### Features

- **Typed end to end** — every request and response is a Pydantic v2 model, and the whole library
  passes `mypy --strict`. Your editor knows the shape of everything you touch.
- **Async-first** — one `async with BinanceThClient()` gives you REST and WebSocket over `httpx` and
  `websockets`, with deterministic teardown.
- **Money is `Decimal`, always** — prices, quantities, balances, and fees never touch `float`, so you
  don't lose a satang to rounding.
- **Signs and reconnects for you** — HMAC signing, server-time offset (`-1021` auto-resync), and a
  dual-window rate limiter that reads Binance's own `x-mbx-used-weight` headers. WebSockets reconnect
  on their own and re-subscribe.
- **A live, self-syncing order book** — `client.ws.order_book("BTCTHB")` returns a book that seeds from
  a REST snapshot and stays current from the depth stream, re-syncing on any gap.
- **A self-healing order tracker** — `client.user_stream.order_tracker()` keeps your open orders in
  sync from the user-data stream and reconciles against REST whenever the socket drops.
- **Errors you can act on** — a typed exception per HTTP status, with one rule baked in: a `5xx` means
  *unknown*, not *failed* — so you check order state instead of blindly retrying.
- **Binance Thailand-aware** — it knows the GLOBAL vs SITE symbol split and routes WebSocket streams to
  the right host for you.

### Installation

Python 3.12+.

```bash
uv add binance-th        # recommended
pip install binance-th
```

### Quick example

```python
import asyncio

from binance_th import BinanceThClient


async def main() -> None:
    async with BinanceThClient() as client:
        # REST: a depth snapshot
        book = await client.market.depth("BTCTHB", limit=5)
        print("best bid/ask:", book.bids[0], book.asks[0])

        # WebSocket: a local order book that keeps itself in sync
        order_book = await client.ws.order_book("BTCTHB")
        await order_book.wait_synced()
        print("live best bid:", order_book.best_bid())
        # ('2102044.00', '0.01872000')
        await order_book.aclose()

        # WebSocket: stream trades as they happen
        async for trade in client.ws.watch_trades("BTCTHB"):
            print("trade:", trade.price, trade.quantity)
            break


asyncio.run(main())
```

No API key is needed for public market data. For signed calls (account, orders) and the user-data
stream, see [Authentication](docs/getting-started/authentication.md).

### What you get

Everything hangs off one client. Each area is its own namespace:

| Namespace | Auth | What it's for | Key methods |
|-----------|------|---------------|-------------|
| `client` | public | connectivity + metadata | `ping`, `server_time`, `exchange_info`, `symbol_types` |
| `client.market` | public | market data | `depth`, `trades`, `agg_trades`, `klines`, `iter_klines`, `ticker_price`, `ticker_24hr`, `book_ticker` |
| `client.account` | signed | account reads | `account`, `trade_fees`, `user_trades`, `iter_user_trades` |
| `client.wallet` | signed | wallet reads | `deposit_address`, `deposit_history`, `withdraw_history` |
| `client.orders` | signed | order management | `create_order`, `cancel_order`, `query_order`, `open_orders` |
| `client.ws` | public | WebSocket market streams | `watch_depth`, `watch_trades`, `watch_agg_trades`, `watch_klines`, `watch_book_ticker`, `watch_ticker`, `order_book` |
| `client.user_stream` | api-key | user-data stream | `watch_orders`, `watch_account`, `watch_balances`, `order_tracker` |

### Which method do I need?

| I want to… | Use |
|-----------|-----|
| Read the order book once | `client.market.depth(symbol)` |
| Keep a live, synced order book | `client.ws.order_book(symbol)` |
| Stream live trades / candles | `client.ws.watch_trades(symbol)` / `client.ws.watch_klines(symbol)` |
| Place or cancel an order | `client.orders.create_order(...)` / `client.orders.cancel_order(...)` |
| Watch my open orders update live | `client.user_stream.order_tracker()` |
| Read my balances | `client.account.account()` |
| Page through historical candles | `client.market.iter_klines(...)` |
| Know if a symbol is GLOBAL or SITE | `client.symbol_types(symbol=...)` |

### Package layout

```text
binance_th
├── BinanceThClient          → the entry point (async context manager)
│   ├── .market              → MarketClient    · public market data
│   ├── .account             → AccountClient   · signed account reads
│   ├── .wallet              → WalletClient    · signed wallet reads
│   ├── .orders              → OrdersClient    · signed order management
│   ├── .ws                  → StreamClient    · WebSocket market streams + order book
│   └── .user_stream         → UserDataStream  · authenticated user-data stream + order tracker
├── BinanceThConfig          → settings (env vars prefixed BINANCE_TH_)
├── binance_th.models        → typed Pydantic models — Decimal money
└── binance_th.exceptions    → the BinanceThError hierarchy — a 5xx means "unknown", not "failed"
```

### GLOBAL vs SITE symbols

Binance Thailand serves two kinds of symbols: **GLOBAL** (shared with Binance, e.g. `BTCUSDT`) and
**SITE** (region-specific, e.g. `BTCTHB`). They don't always carry the same fields, and their WebSocket
streams live on different hosts. The library surfaces the type (`client.symbol_types(...)`) and routes
streams for you — you just pass the symbol. See [GLOBAL vs SITE](docs/concepts/global-vs-site.md).

### Errors

Every failure is a typed exception, so you can catch exactly what you mean:

| Exception | When | What to do |
|-----------|------|-----------|
| `BinanceThBadRequestError` (400) | bad params | fix the request |
| `BinanceThAuthError` (401) | bad key / signature / clock | check credentials |
| `BinanceThRateLimitError` (429) | too many requests | back off (`retry_after`) |
| `BinanceThServerError` (5xx) | server error | **status is UNKNOWN — check before retrying** |
| `BinanceThOrderUnknownError` | order sent, outcome unclear | resubmit only if `resubmittable` is `True` |

More in [Errors & reconciliation](docs/concepts/errors-and-reconciliation.md).

### For AI agents

This library is designed to be consumed by AI agents. Start with **[`llms.txt`](llms.txt)** — a single,
structured map of the whole public surface (namespaces, methods, conventions, and one example each).
The [reference](docs/reference/index.md) pages are spec-style (signature → parameters → returns → raises
→ example) so exact signatures are easy to quote. One thing to keep in mind: the **signed** (account,
wallet, order) and **user-data event** models are marked ⚠ASSUMED where they haven't been verified
against the live API — don't over-trust those field shapes. See
[Assumed shapes](docs/concepts/assumed-shapes.md).

### Documentation

Full docs live in [`docs/`](docs/index.md):

- **Getting started** — [Installation](docs/getting-started/installation.md) ·
  [Quickstart](docs/getting-started/quickstart.md) · [Authentication](docs/getting-started/authentication.md)
- **Concepts** — [GLOBAL vs SITE](docs/concepts/global-vs-site.md) ·
  [Money & Decimals](docs/concepts/money-and-decimals.md) ·
  [Errors & reconciliation](docs/concepts/errors-and-reconciliation.md) ·
  [Rate limiting](docs/concepts/rate-limiting.md) · [WebSockets](docs/concepts/websockets.md) ·
  [Assumed shapes](docs/concepts/assumed-shapes.md)
- **Guides** — [Market data](docs/guides/market-data.md) · [Orders](docs/guides/orders.md) ·
  [Market streams](docs/guides/market-streams.md) · [Local order book](docs/guides/local-order-book.md) ·
  [User-data stream](docs/guides/user-data-stream.md) · [Pagination](docs/guides/pagination.md)
- **Reference** — [API reference](docs/reference/index.md)
- **Architecture** — [Overview](docs/architecture/overview.md) and the
  [ADRs](docs/plans/adr/README.md)

### Project status

- [x] **Phase 1: Foundation** — core models, exceptions, configuration
- [x] **Phase 2: Authentication & Rate Limiting** — HMAC signatures, server-time offset, dual-window token bucket
- [x] **Phase 3: REST API Client** — market, account/wallet reads + orders (create/cancel/query)
- [x] **Phase 4: WebSocket Market Streams** — depth/trade/aggTrade/kline/bookTicker/ticker + self-syncing local order book (live-verified)
- [x] **Phase 5: User-Data Stream** — listenKey manager (dual GLOBAL/SITE keys), account/order events, self-healing order tracker (live-verified)
- [x] **Phase 6: Documentation & Release** — docs, security scanning (bandit/pip-audit), PyPI publish workflow — `1.0.0`

Available now in both English and Thai.

### Why binance-th

There was no typed, async, Thailand-specific client that got the tricky parts right — the GLOBAL/SITE
split, the "a 5xx is unknown, not failed" order rule, the self-syncing order book, and credential
hygiene. binance-th does, and it was built endpoint-by-endpoint against the live API so the shapes match
reality (the few that couldn't be verified live are marked clearly).

### Stability

`1.0.0` follows [Semantic Versioning](https://semver.org/). The public API (the client namespaces,
models, and exceptions above) is stable across the `1.x` line.

### Contributing

Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). The quality gate before every commit:

```bash
uv run pytest                       # full suite, >=90% coverage
uv run ruff format . && uv run ruff check . --fix
uv run mypy binance_th              # strict
```

### License

MIT — see [LICENSE](LICENSE).

---

## ภาษาไทย

> โค้ด ชื่อฟังก์ชัน/ตัวแปร และ endpoint path ทั้งหมด เขียนเป็นภาษาอังกฤษตามต้นฉบับ

binance-th — ไลบรารี Python แบบ async สำหรับ **Binance Thailand** ทั้ง REST และ WebSocket พร้อม type ครบ

คุยกับ exchange ด้วย `async`/`await` ตรง ๆ เลย — ส่งออเดอร์ ดึงข้อมูลตลาด และเกาะดู depth, trade,
รวมถึงบัญชีของคุณเองแบบเรียลไทม์ผ่าน WebSocket ได้ ทุก payload เป็น Pydantic model ที่มี type ชัดเจน
ทุกราคาเป็น `Decimal` เหมาะกับเครื่องมือเทรด, data pipeline และ AI agent

### คุณสมบัติ

- **Type ครบทั้งเส้นทาง** — ทุก request และ response เป็น Pydantic v2 model และทั้งไลบรารีผ่าน
  `mypy --strict` editor ของคุณจะรู้หน้าตาข้อมูลทุกอย่างที่คุณแตะ
- **Async เป็นหลัก** — แค่ `async with BinanceThClient()` ก็ได้ทั้ง REST และ WebSocket บน `httpx`
  และ `websockets` พร้อมปิดการเชื่อมต่อให้เรียบร้อยอัตโนมัติ
- **เงินเป็น `Decimal` เสมอ** — ราคา จำนวน ยอดคงเหลือ และค่าธรรมเนียม ไม่แตะ `float` เลย
  คุณจะไม่เสียแม้แต่สตางค์เดียวเพราะการปัดเศษ
- **เซ็นและ reconnect ให้เอง** — เซ็น HMAC, ชดเชยเวลาเซิร์ฟเวอร์ (resync `-1021` อัตโนมัติ) และ
  rate limiter แบบสองหน้าต่างที่อ่านส่วนหัว `x-mbx-used-weight` ของ Binance เอง ส่วน WebSocket ก็
  reconnect และ subscribe ใหม่ให้เองเมื่อหลุด
- **Order book ที่ซิงก์ตัวเอง** — `client.ws.order_book("BTCTHB")` คืนสมุดคำสั่งที่เริ่มจาก snapshot
  ทาง REST แล้วอัปเดตต่อเนื่องจาก depth stream พร้อมซิงก์ใหม่ทันทีถ้าข้อมูลขาดช่วง
- **Order tracker ที่ซ่อมแซมตัวเอง** — `client.user_stream.order_tracker()` เกาะออเดอร์ที่เปิดอยู่ของคุณ
  ให้ตรงกับความจริงจาก user-data stream และ reconcile กับ REST ทุกครั้งที่ socket หลุด
- **Error ที่จัดการต่อได้จริง** — มี exception แยกตาม HTTP status พร้อมกฎสำคัญข้อหนึ่ง: `5xx` แปลว่า
  *ไม่รู้ผล* ไม่ใช่ *ล้มเหลว* — ให้เช็คสถานะออเดอร์ก่อน อย่าเพิ่งลองใหม่มั่ว ๆ
- **เข้าใจ Binance Thailand** — รู้จักการแยกสัญลักษณ์ GLOBAL กับ SITE และจัดเส้นทาง WebSocket ไปโฮสต์
  ที่ถูกต้องให้คุณเอง แค่ส่งชื่อสัญลักษณ์มาพอ

### การติดตั้ง

ต้องใช้ Python 3.12 ขึ้นไป

```bash
uv add binance-th        # แนะนำ
pip install binance-th
```

### ตัวอย่างเริ่มต้น

```python
import asyncio

from binance_th import BinanceThClient


async def main() -> None:
    async with BinanceThClient() as client:
        # REST: ขอ snapshot ของ order book
        book = await client.market.depth("BTCTHB", limit=5)
        print("best bid/ask:", book.bids[0], book.asks[0])

        # WebSocket: order book ที่ซิงก์ตัวเอง
        order_book = await client.ws.order_book("BTCTHB")
        await order_book.wait_synced()
        print("live best bid:", order_book.best_bid())
        await order_book.aclose()

        # WebSocket: สตรีม trade แบบเรียลไทม์
        async for trade in client.ws.watch_trades("BTCTHB"):
            print("trade:", trade.price, trade.quantity)
            break


asyncio.run(main())
```

ข้อมูลตลาดสาธารณะไม่ต้องใช้ API key ส่วนคำสั่งที่ต้องเซ็น (บัญชี, ออเดอร์) และ user-data stream ดูได้ที่
[Authentication](docs/getting-started/authentication.md)

### มีอะไรให้ใช้บ้าง

ทุกอย่างอยู่ใต้ client เดียว แต่ละส่วนเป็น namespace ของตัวเอง:

| Namespace | สิทธิ์ | ใช้ทำอะไร | เมธอดหลัก |
|-----------|--------|-----------|-----------|
| `client` | สาธารณะ | เช็คการเชื่อมต่อ + ข้อมูลระบบ | `ping`, `server_time`, `exchange_info`, `symbol_types` |
| `client.market` | สาธารณะ | ข้อมูลตลาด | `depth`, `trades`, `klines`, `iter_klines`, `ticker_price`, `book_ticker` |
| `client.account` | ต้องเซ็น | อ่านข้อมูลบัญชี | `account`, `trade_fees`, `user_trades`, `iter_user_trades` |
| `client.wallet` | ต้องเซ็น | อ่านข้อมูลกระเป๋า | `deposit_address`, `deposit_history`, `withdraw_history` |
| `client.orders` | ต้องเซ็น | จัดการออเดอร์ | `create_order`, `cancel_order`, `query_order`, `open_orders` |
| `client.ws` | สาธารณะ | สตรีมข้อมูลตลาด | `watch_depth`, `watch_trades`, `watch_klines`, `order_book` |
| `client.user_stream` | ใช้ api-key | user-data stream | `watch_orders`, `watch_account`, `watch_balances`, `order_tracker` |

### สถานะโปรเจกต์

- [x] **Phase 1: รากฐาน** — โมเดลหลัก, exceptions, การตั้งค่า
- [x] **Phase 2: การยืนยันตัวตนและการจำกัดอัตรา** — ลายเซ็น HMAC, ชดเชยเวลาเซิร์ฟเวอร์, token bucket แบบสองหน้าต่าง
- [x] **Phase 3: REST API Client** — market, อ่านบัญชี/กระเป๋า + ออเดอร์ (create/cancel/query)
- [x] **Phase 4: WebSocket Market Streams** — depth/trade/aggTrade/kline/bookTicker/ticker + order book ที่ซิงก์ตัวเอง (ตรวจสอบกับ feed จริงแล้ว)
- [x] **Phase 5: User-Data Stream** — ตัวจัดการ listenKey (คีย์ GLOBAL/SITE คู่), เหตุการณ์บัญชี/ออเดอร์, order tracker ที่ซ่อมแซมตัวเอง (ตรวจสอบกับ feed จริงแล้ว)
- [x] **Phase 6: เอกสารและการเผยแพร่** — เอกสาร, สแกนความปลอดภัย (bandit/pip-audit), workflow เผยแพร่บน PyPI — `1.0.0`

พร้อมใช้งานแล้วทั้งภาษาอังกฤษและภาษาไทย

### เอกสาร

เอกสารฉบับเต็ม (ภาษาอังกฤษ) อยู่ที่ [`docs/`](docs/index.md) — เริ่มที่
[Quickstart](docs/getting-started/quickstart.md) หรือ [API reference](docs/reference/index.md)
สำหรับ AI agent เริ่มที่ [`llms.txt`](llms.txt)

### สัญญาอนุญาต

MIT — ดู [LICENSE](LICENSE)
