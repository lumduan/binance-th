# Pagination

[Home](../index.md) > Guides > Pagination

Some history is longer than a single call can return. The `iter_*` methods page through it for you and
hand back one async stream of de-duplicated results.

## Prerequisites

- [Market data](market-data.md) / [Authentication](../getting-started/authentication.md) (for signed
  history)

---

## Klines over a long range

`iter_klines` walks a `[start_time, end_time)` window in `limit`-sized pages (both are epoch
milliseconds):

```python
candles = []
async for k in client.market.iter_klines(
    "BTCTHB", "1h",
    start_time=1700000000000,
    end_time=1700604800000,      # ~1 week later
    limit=1000,
):
    candles.append(k)
print(len(candles))
```

Collect into a list with a comprehension if you prefer:

```python
candles = [k async for k in client.market.iter_klines("BTCTHB", "1d",
                                                       start_time=start_ms, end_time=end_ms)]
```

## Trade and deposit history

The same shape applies to signed history:

```python
# your trades on a symbol
trades = [t async for t in client.account.iter_user_trades(
    "BTCTHB", start_time=start_ms, end_time=end_ms)]

# deposit history
deposits = [d async for d in client.wallet.iter_deposit_history(
    coin="THB", start_time=start_ms, end_time=end_ms)]
```

Each iterator advances by the last item's timestamp/id and drops duplicates across page boundaries, so
you get a clean, ordered stream.

## Single-call variants

When a window fits in one response, the non-iterator methods (`klines`, `user_trades`,
`deposit_history`) return a plain `list` — reach for those when you don't need paging.

> Note: withdraw history is single-call only (`withdraw_history`); there is no `iter_withdraw_history`.

## See Also

- [Market data guide](market-data.md)
- [Reference: market](../reference/market.md) · [account](../reference/account.md) ·
  [wallet](../reference/wallet.md)
