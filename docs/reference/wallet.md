# WalletClient Reference

[Home](../index.md) > Reference > wallet

**Module:** `binance_th.wallet` · **Available since:** 1.0.0

Signed wallet reads (`client.wallet`) — deposit addresses and deposit/withdrawal history. Every method
is **signed**. This namespace is read-only in 1.0.0; it does not move funds.

> ⚠ **Assumed shapes.** Deposit/withdrawal models follow the documented schema but are not all confirmed
> against live responses; unknown fields are preserved (`extra="allow"`). See
> [Assumed shapes](../concepts/assumed-shapes.md).

## Import

Accessed as `client.wallet`. Requires credentials.

## Methods

### deposit_address

```python
async def deposit_address(coin: str, *, network: str | None = None) -> DepositAddress
```
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `coin` | `str` | — | e.g. `"USDT"` |
| `network` | `str \| None` | `None` | chain, when a coin has several |

**Signed.** **Returns** `DepositAddress` (`.address`, `.coin`, `.tag`, `.url`).

### deposit_history

```python
async def deposit_history(*, coin: str | None = None, start_time: int | None = None,
                          end_time: int | None = None, limit: int | None = None) -> list[DepositRecord]
```
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `coin` | `str \| None` | `None` | filter by coin |
| `start_time` / `end_time` | `int \| None` | `None` | epoch ms |
| `limit` | `int \| None` | `None` | max records |

**Signed.** **Returns** `list[DepositRecord]` (paginates on the integer `insert_time`).

### iter_deposit_history

```python
async def iter_deposit_history(*, coin: str | None = None, start_time: int,
                               end_time: int, limit: int = 1000) -> AsyncIterator[DepositRecord]
```
**Signed.** Async generator paging deposit history across `[start_time, end_time)` (**required**, epoch
ms), de-duplicating by `tx_id`. Consume with `async for`. **Yields** `DepositRecord`.

### withdraw_history

```python
async def withdraw_history(*, coin: str | None = None, start_time: int | None = None,
                           end_time: int | None = None, limit: int | None = None) -> list[WithdrawRecord]
```
**Signed.** **Returns** `list[WithdrawRecord]`. There is no `iter_withdraw_history` in 1.0.0 —
`WithdrawRecord.apply_time` is a string with no integer timestamp to page on, so page manually with
`start_time`/`end_time` if needed.

## See Also

- [Authentication](../getting-started/authentication.md) · [account](account.md)
- [models](models.md) · [Assumed shapes](../concepts/assumed-shapes.md)
