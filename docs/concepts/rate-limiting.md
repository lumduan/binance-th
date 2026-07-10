# Rate limiting

[Home](../index.md) > Concepts > Rate limiting

**English** · [ไทย](../th/concepts/rate-limiting.md)

binance-th paces your requests so you stay under Binance Thailand's limits, and it corrects itself from
the exchange's own counters. It's on by default; you rarely think about it.

## Two windows

Binance enforces two kinds of budget at once — a **request-weight** budget (each endpoint costs a
weight) and an **order-count** budget. The limiter tracks both windows and waits when either would be
exceeded, rather than letting you trip a `429`.

## Reconciled from response headers

Every REST response carries `x-mbx-used-weight-1m` (the weight the server has actually counted). The
limiter reads that header and trues up its own estimate, so it stays accurate even if some requests
were heavier than expected. The authoritative limits themselves are adopted from
`client.exchange_info()` the first time you call it.

## If you do hit a limit

A `429` raises `BinanceThRateLimitError` with `retry_after` and `used_weight`; repeated violations can
escalate to a `418` (`BinanceThIPBannedError`) with a longer `retry_after`. Both tell you how long to
wait.

```python
from binance_th import BinanceThRateLimitError

try:
    await client.market.depth("BTCTHB")
except BinanceThRateLimitError as e:
    await asyncio.sleep(e.retry_after or 1)
```

## Turning it off

```python
from binance_th import BinanceThConfig
config = BinanceThConfig(enable_rate_limiting=False)   # you now manage pacing yourself
```

Leave it on unless you have your own limiter in front.

## See Also

- [Errors & reconciliation](errors-and-reconciliation.md)
- [Reference: config](../reference/config.md)
