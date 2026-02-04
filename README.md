# binance-th

A production-ready Python async library for Binance Thailand API.

## Features

- **Type-Safe**: Complete type annotations using Pydantic models
- **Async-First**: All I/O operations use async/await patterns
- **Modern Python**: Supports Python 3.12+
- **Comprehensive Error Handling**: Typed exception hierarchy for precise error handling
- **Rate Limiting**: Built-in rate limiting with automatic backoff (planned)
- **WebSocket Support**: Real-time market data and user streams (planned)

## Installation

```bash
pip install binance-th
```

## Quick Start

```python
from binance_th import BinanceThConfig
from binance_th.models import OrderSide, OrderType

# Create configuration
config = BinanceThConfig(
    api_key="your_api_key",
    api_secret="your_api_secret",
)

# REST client will be available in Phase 2+
```

## Project Status

This library is under active development.

- [x] **Phase 1: Foundation** - Core models, exceptions, configuration
- [ ] **Phase 2: Authentication & Rate Limiting** - HMAC signatures, token bucket
- [ ] **Phase 3: REST API Client** - Full REST API coverage
- [ ] **Phase 4: WebSocket Client** - Market streams, user data streams
- [ ] **Phase 5: Documentation & Release** - Full documentation, PyPI release

## Documentation

See the [API documentation](https://www.binance.th/api-docs/en/?python) for details on Binance Thailand API.

## License

MIT
