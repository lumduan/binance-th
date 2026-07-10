# BinanceThClient Reference

[Home](../index.md) > Reference > client

**Module:** `binance_th.client` · **Available since:** 1.0.0

The async entry point. Owns the HTTP + WebSocket connections and exposes the sub-clients. Use it as an
async context manager.

## Import

```python
from binance_th import BinanceThClient, BinanceThConfig
```

## Constructor

```python
BinanceThClient(config: BinanceThConfig | None = None, *, transport: Transport | None = None)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `config` | `BinanceThConfig \| None` | `None` | Settings; defaults to `BinanceThConfig()` (reads `BINANCE_TH_*` env / `.env`). |
| `transport` | `Transport \| None` | `None` | Keyword-only injection seam (for tests); leave unset. |

```python
async with BinanceThClient() as client:
    ...
```

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `client.market` | `MarketClient` | [public market data](market.md) |
| `client.account` | `AccountClient` | [signed account reads](account.md) |
| `client.wallet` | `WalletClient` | [signed wallet reads](wallet.md) |
| `client.orders` | `OrdersClient` | [signed order management](orders.md) |
| `client.ws` | `StreamClient` | [WebSocket market streams](streams.md) |
| `client.user_stream` | `UserDataStream` | [user-data stream](user-stream.md) |
| `client.is_closed` | `bool` | True once closed. |

## Methods

### ping

```python
async def ping() -> bool
```
`GET /api/v1/ping`. Public. Returns `True` if the API answers. **Returns** `bool`.

### server_time

```python
async def server_time() -> ServerTime
```
`GET /api/v1/time`. Public; also refreshes the internal signing time-offset. **Returns** `ServerTime`.

### exchange_info

```python
async def exchange_info(*, force: bool = False) -> ExchangeInfo
```
`GET /api/v1/exchangeInfo`. Cached after the first call; also seeds the rate limiter. Pass `force=True`
to re-fetch. **Returns** `ExchangeInfo` (use `.get_symbol(sym)` for a `SymbolInfo`).

### symbol_types

```python
async def symbol_types(*, symbol: str | None = None) -> list[SymbolTypeInfo]
```
`GET /api/v1/symbolType`. Public. GLOBAL/SITE type per symbol; always a list. Pass `symbol=` to filter.
**Returns** `list[SymbolTypeInfo]`.

### aclose

```python
async def aclose() -> None
```
Closes market streams, then the user-data stream, then the transport. Idempotent. Called automatically
on `async with` exit.

## See Also

- [Quickstart](../getting-started/quickstart.md)
- [config](config.md) · [exceptions](exceptions.md)
