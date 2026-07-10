# MarketClient Reference

[Home](../index.md) > Reference > market

**English** · [ไทย](../th/reference/market.md)

**Module:** `binance_th.market` · **Available since:** 1.0.0

Public market data (`client.market`). No credentials required. Money fields are `Decimal`.

## Import

Accessed as `client.market`.

## Methods

### depth

```python
async def depth(symbol: str, *, limit: int | None = None) -> OrderBook
```
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | `str` | — | e.g. `"BTCTHB"` |
| `limit` | `int \| None` | `None` | number of levels per side |

**Returns** `OrderBook` (`.last_update_id`, `.bids`, `.asks` — each an `OrderBookEntry` with `.price`/`.quantity`).

### trades

```python
async def trades(symbol: str, *, limit: int | None = None) -> list[Trade]
```
Recent trades. **Returns** `list[Trade]`.

### agg_trades

```python
async def agg_trades(symbol: str, *, limit: int | None = None) -> list[AggregateTrade]
```
Compressed aggregate trades. **Returns** `list[AggregateTrade]`.

### klines

```python
async def klines(symbol: str, interval: KlineInterval | str, *,
                 limit: int | None = None, start_time: int | None = None,
                 end_time: int | None = None) -> list[Kline]
```
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `interval` | `KlineInterval \| str` | — | e.g. `KlineInterval.HOUR_1` or `"1h"` |
| `limit` | `int \| None` | `None` | max candles |
| `start_time` / `end_time` | `int \| None` | `None` | epoch ms |

**Returns** `list[Kline]`. For long ranges use [`iter_klines`](#iter_klines).

### iter_klines

```python
async def iter_klines(symbol: str, interval: KlineInterval | str, *,
                      start_time: int, end_time: int, limit: int = 1000) -> AsyncIterator[Kline]
```
Async generator that pages `[start_time, end_time)` and de-duplicates by open time. `start_time` and
`end_time` are **required** (epoch ms). Consume with `async for` — do not `await` the call. **Yields**
`Kline`.

```python
candles = [k async for k in client.market.iter_klines("BTCTHB", "1h",
                                                       start_time=s, end_time=e)]
```

### ticker_price

```python
async def ticker_price(symbol: str) -> PriceTicker
```
Latest price. **Returns** `PriceTicker` (`.price: Decimal`).

### ticker_24hr

```python
async def ticker_24hr(symbol: str) -> Ticker24hr
```
24-hour rolling statistics. **Returns** `Ticker24hr`. Note: several fields are `null` on SITE symbols.

### book_ticker

```python
async def book_ticker(symbol: str) -> BookTicker
```
Best bid/ask. **Returns** `BookTicker` (`.bid_price`, `.bid_qty`, `.ask_price`, `.ask_qty`).

### reference_price

```python
async def reference_price(symbol: str) -> ReferencePrice
```
**GLOBAL symbols only.** **Raises** `BinanceThBadRequestError` for a SITE/THB symbol.

### execution_rules

```python
async def execution_rules() -> ExecutionRules
```
Per-symbol execution rules. **GLOBAL only.** **Returns** `ExecutionRules` (`.get_symbol(sym)`).

## See Also

- [Market data guide](../guides/market-data.md) · [Pagination guide](../guides/pagination.md)
- [models](models.md) · [GLOBAL vs SITE](../concepts/global-vs-site.md)
