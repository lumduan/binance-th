# Testing

[Home](../index.md) > Development > Testing

**English** · [ไทย](../th/development/testing.md)

## Running the suite

```bash
uv run pytest
```

Coverage is enforced: `[tool.pytest.ini_options] addopts` hard-codes `--cov-fail-under=90`, so the whole
suite must keep **≥ 90%** coverage or pytest exits non-zero.

## Running a single test — the coverage gotcha

Because coverage is measured across the whole package, running a **subset** makes coverage look low and
pytest exits non-zero **even when the selected tests pass**. Disable coverage for a focused run:

```bash
uv run pytest tests/test_models/test_orders.py::TestOrderRequest::test_valid_limit_order --no-cov
```

Use `--no-cov` whenever you run less than the full suite; drop it (run everything) before you push.

## What the tests assert

- **Order-rule validators** assert on the exact `ValueError` message strings (LIMIT ⇒ price + timeInForce
  + quantity; MARKET ⇒ quantity **or** quoteOrderQty; STOP\* ⇒ stopPrice; cancel/query ⇒ `orderId` **or**
  `origClientOrderId`). Change a message and the test changes with it.
- **Alias round-trips** — models accept both snake_case and the camelCase wire alias.
- **Array parsers** — `Kline.from_list`, `OrderBookEntry.from_list`, `OrderBook.from_api`.
- **Error mapping** — status code → the right exception class.

## Live probes and soaks (opt-in, not part of CI)

`scripts/probe_ws.py`, `scripts/probe_userdata.py`, and `scripts/soak_userdata.py` exercise the live API
with real credentials — `soak_userdata.py` can place and manage **real orders**. They are guarded and
opt-in; never wire them into automated runs. They exist to verify the [assumed shapes](../concepts/assumed-shapes.md).

## See Also

- [Contributing](contributing.md) · [Release process](release-process.md)
