# AccountClient Reference

[Home](../index.md) > Reference > account

**English** · [ไทย](../th/reference/account.md)

**Module:** `binance_th.account` · **Available since:** 1.0.0

Signed account reads (`client.account`). Every method here is **signed** — it needs an API key and
secret; the client signs each request for you. Money fields are `Decimal`.

> ⚠ **Assumed shapes.** These response models are built from the documented Binance-TH schema but have
> not all been confirmed against live signed responses. Unknown fields are preserved
> (`extra="allow"`), so nothing is dropped — but treat field names as provisional until verified. See
> [Assumed shapes](../concepts/assumed-shapes.md).

## Import

Accessed as `client.account`. Requires credentials — see [Authentication](../getting-started/authentication.md).

## Methods

### account

```python
async def account() -> AccountInfo
```
Account status and balances. **Signed.** **Returns** `AccountInfo` (`.balances` — each `Balance` has
`.asset`, `.free: Decimal`, `.locked: Decimal`). **Raises** `BinanceThAuthError` if credentials are
missing/invalid.

```python
info = await client.account.account()
for b in info.balances:
    if b.free or b.locked:
        print(b.asset, b.free, b.locked)
```

### trade_fees

```python
async def trade_fees(*, symbol: str | None = None) -> list[TradeFee]
```
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | `str \| None` | `None` | one symbol, or all when omitted |

**Signed.** **Returns** `list[TradeFee]` (`.symbol`, `.maker_commission`, `.taker_commission`).

### user_trades

```python
async def user_trades(symbol: str, *, limit: int | None = None,
                      start_time: int | None = None, end_time: int | None = None) -> list[UserTrade]
```
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | `str` | — | required |
| `limit` | `int \| None` | `None` | max trades |
| `start_time` / `end_time` | `int \| None` | `None` | epoch ms |

**Signed.** Your own fills for one symbol. **Returns** `list[UserTrade]`. For a full range use
[`iter_user_trades`](#iter_user_trades).

### iter_user_trades

```python
async def iter_user_trades(symbol: str, *, start_time: int, end_time: int,
                           limit: int = 1000) -> AsyncIterator[UserTrade]
```
**Signed.** Async generator that pages your trade history across `[start_time, end_time)`
(**required**, epoch ms) and de-duplicates by trade id. Consume with `async for`. **Yields** `UserTrade`.

```python
fills = [t async for t in client.account.iter_user_trades("BTCTHB")]
```

## See Also

- [Authentication](../getting-started/authentication.md) · [Pagination guide](../guides/pagination.md)
- [wallet](wallet.md) · [models](models.md) · [Assumed shapes](../concepts/assumed-shapes.md)
