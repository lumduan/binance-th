# API Reference

[Home](../index.md) > Reference

**Available since:** 1.0.0. Every method's exact signature, parameters, and return type. For narrative,
see the [guides](../guides/market-data.md); for the whole surface on one page, [`llms.txt`](../../llms.txt).

## Package tree

```text
binance_th
├── BinanceThClient                → the async entry point       → reference/client.md
│   ├── .market   → MarketClient    → public market data         → reference/market.md
│   ├── .account  → AccountClient   → signed account reads        → reference/account.md
│   ├── .wallet   → WalletClient    → signed wallet reads         → reference/wallet.md
│   ├── .orders   → OrdersClient    → signed order management     → reference/orders.md
│   ├── .ws       → StreamClient    → WebSocket market streams    → reference/streams.md
│   └── .user_stream → UserDataStream → user-data stream          → reference/user-stream.md
├── BinanceThConfig                 → settings                    → reference/config.md
├── binance_th.exceptions           → error hierarchy             → reference/exceptions.md
└── binance_th.models               → Pydantic models + enums     → reference/models.md
```

## Namespaces

| Page | Class | Auth | Methods |
|------|-------|------|---------|
| [client](client.md) | `BinanceThClient` | public | `ping`, `server_time`, `exchange_info`, `symbol_types`, `aclose` |
| [market](market.md) | `MarketClient` | public | `depth`, `trades`, `agg_trades`, `klines`, `iter_klines`, `ticker_price`, `ticker_24hr`, `book_ticker`, `reference_price`, `execution_rules` |
| [account](account.md) | `AccountClient` | signed | `account`, `trade_fees`, `user_trades`, `iter_user_trades` |
| [wallet](wallet.md) | `WalletClient` | signed | `deposit_address`, `deposit_history`, `iter_deposit_history`, `withdraw_history` |
| [orders](orders.md) | `OrdersClient` | signed | `create_order`, `cancel_order`, `query_order`, `open_orders` |
| [streams](streams.md) | `StreamClient`, `ManagedOrderBook` | public | `watch_depth/trades/agg_trades/klines/book_ticker/ticker`, `order_book` |
| [user-stream](user-stream.md) | `UserDataStream`, `OrderTracker` | api-key | `watch_orders/account/balances`, `order_tracker` |
| [config](config.md) | `BinanceThConfig` | — | all settings + env vars |
| [exceptions](exceptions.md) | `BinanceThError` … | — | the exception hierarchy |
| [models](models.md) | Pydantic models + enums | — | exported models, enum value sets, `from_list`/`from_api` |

## Quick navigation: which page do I need?

| I want to… | Go to |
|-----------|-------|
| Read the order book (once / live) | [market](market.md) `depth` / [streams](streams.md) `order_book` |
| Stream trades, candles, tickers | [streams](streams.md) |
| Place / cancel / query an order | [orders](orders.md) |
| Read balances or trade history | [account](account.md) |
| Deposit address / history | [wallet](wallet.md) |
| Follow my orders in real time | [user-stream](user-stream.md) |
| Configure credentials / URLs / limits | [config](config.md) |
| Handle an error | [exceptions](exceptions.md) |
| Know a model's fields or an enum's values | [models](models.md) |

## See Also

- [Documentation home](../index.md)
- [`llms.txt`](../../llms.txt) — the whole surface, condensed for AI agents
