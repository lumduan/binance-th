# Installation

[Home](../index.md) > Getting Started > Installation

**English** · [ไทย](../th/getting-started/installation.md)

binance-th needs **Python 3.12 or newer**.

## Install

```bash
uv add binance-th        # recommended
pip install binance-th
```

That's everything for public market data and WebSocket streams. The runtime dependencies —
`httpx`, `pydantic`, `pydantic-settings`, and `websockets` — come along automatically.

## Verify

```bash
python -c "import binance_th; print(binance_th.__version__)"
# 1.0.0
```

## Type checking

binance-th ships a `py.typed` marker, so `mypy` and your editor pick up its types with no extra setup.

## See Also

- [Quickstart](quickstart.md) — your first script
- [Authentication](authentication.md) — needed only for signed calls and the user-data stream
