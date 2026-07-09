"""Binance Thailand Python Library.

A production-ready Python async library for Binance Thailand API.
Supports both REST API and WebSocket connections with comprehensive
error handling, rate limiting, and retry mechanisms.

Features:
- Type-safe with Pydantic models
- Async-first architecture
- Comprehensive error handling
- Rate limiting with automatic backoff
- WebSocket support with reconnection

Example:
    >>> from binance_th import BinanceThConfig
    >>> from binance_th.models import OrderSide, OrderType
    >>>
    >>> config = BinanceThConfig(
    ...     api_key="your_api_key",
    ...     api_secret="your_api_secret",
    ... )

Note:
    REST client and WebSocket client will be available in future phases.
"""

from binance_th.client import BinanceThClient
from binance_th.config import BinanceThConfig
from binance_th.exceptions import (
    BinanceThAPIError,
    BinanceThAuthError,
    BinanceThBadRequestError,
    BinanceThError,
    BinanceThIPBannedError,
    BinanceThNetworkError,
    BinanceThRateLimitError,
    BinanceThServerError,
    BinanceThTimeoutError,
    BinanceThValidationError,
    BinanceThWAFError,
    BinanceThWebSocketError,
)
from binance_th.models import (
    KlineInterval,
    OrderSide,
    OrderStatus,
    OrderType,
    TimeInForce,
)

__version__ = "0.1.0"

__all__ = [
    "BinanceThAPIError",
    "BinanceThAuthError",
    "BinanceThBadRequestError",
    # Client
    "BinanceThClient",
    # Config
    "BinanceThConfig",
    # Exceptions
    "BinanceThError",
    "BinanceThIPBannedError",
    "BinanceThNetworkError",
    "BinanceThRateLimitError",
    "BinanceThServerError",
    "BinanceThTimeoutError",
    "BinanceThValidationError",
    "BinanceThWAFError",
    "BinanceThWebSocketError",
    "KlineInterval",
    # Common Enums (for convenience)
    "OrderSide",
    "OrderStatus",
    "OrderType",
    "TimeInForce",
    # Version
    "__version__",
]
