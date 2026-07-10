# Assumed shapes

[Home](../index.md) > Concepts > Assumed shapes

binance-th was built endpoint-by-endpoint against the live API, so most response models match reality
exactly. A few couldn't be verified live yet — those are marked **⚠ ASSUMED**, and it's worth knowing
which so you don't over-trust their exact field sets.

## What's verified vs assumed

| Area | Status |
|------|--------|
| Public REST (market data) | ✅ live-verified |
| Market WebSocket streams (depth/trade/kline/ticker) | ✅ live-verified |
| listenKey lifecycle + user-data connection | ✅ live-verified |
| Signed reads (`account`, `wallet`) | ⚠ ASSUMED — modelled, not verified against a credentialed response |
| Orders (`create`/`cancel`/`query`) | ⚠ ASSUMED — mock-tested only (they move real money) |
| User-data **events** (`executionReport`, `outboundAccountPosition`, `balanceUpdate`) | ⚠ ASSUMED — the probe saw the stream connect but no event fired on an idle account |

## Why it's safe to use anyway

- Response models use `extra="allow"`, so any field the exchange sends that isn't modelled is
  **preserved**, never dropped or errored — you can always read it via the model's extras.
- Enum-like fields on user-data events are typed as **raw `str`**, not the library enums, so an
  unexpected value (e.g. a status like `PENDING_CANCEL`) can't crash decoding.

The practical caution: treat the exact field *names/types* on the ⚠ areas as provisional. Read what you
need defensively, and don't assume a field is present just because the model lists it.

## Verifying it yourself

The repository ships a guarded, opt-in script that finally confirms the user-data event shapes by
placing one tiny, far-from-market order (so it rests and cancels without filling), capturing the real
`executionReport`, then cancelling:

```bash
BINANCE_TH_SOAK=1 uv run python scripts/soak_userdata.py
```

It refuses to run without both `BINANCE_TH_SOAK=1` and credentials, and it never fills — but it does
place a **real** order, so read the script first. If you run it, the captured shapes can be folded back
into the models.

## See Also

- [Orders guide](../guides/orders.md)
- [User-data stream guide](../guides/user-data-stream.md)
- [GLOBAL vs SITE](global-vs-site.md)
