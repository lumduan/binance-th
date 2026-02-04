"""Configuration management for Binance Thailand API client.

This module provides a pydantic-settings based configuration class
that supports loading from environment variables and .env files.

Example:
    # Using environment variables
    export BINANCE_TH_API_KEY="your_key"
    export BINANCE_TH_API_SECRET="your_secret"

    # Using in code
    from binance_th.config import BinanceThConfig
    config = BinanceThConfig()

    # Or with direct instantiation
    config = BinanceThConfig(
        api_key="your_key",
        api_secret="your_secret",
    )
"""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class BinanceThConfig(BaseSettings):
    """Configuration for Binance Thailand API client.

    Can be configured via:
    - Environment variables (BINANCE_TH_* prefix)
    - .env file
    - Direct instantiation

    Attributes:
        api_key: API key for authenticated endpoints
        api_secret: API secret for signed endpoints (stored securely)
        rest_base_url: Base URL for REST API
        ws_base_url_global: WebSocket URL for GLOBAL symbols
        ws_base_url_site: WebSocket URL for SITE symbols
        timeout: Request timeout in seconds
        max_retries: Maximum retries for transient errors
        enable_rate_limiting: Enable automatic rate limiting
        recv_window: Request validity window in milliseconds (default 5000, max 60000)
        ws_auto_reconnect: Enable automatic WebSocket reconnection
        ws_ping_interval: WebSocket ping interval in seconds
        ws_ping_timeout: WebSocket ping timeout in seconds
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_requests: Log all API requests (for debugging)
        log_responses: Log all API responses (for debugging)
    """

    model_config = SettingsConfigDict(
        env_prefix="BINANCE_TH_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Credentials
    api_key: str | None = Field(
        default=None,
        description="API key for authenticated endpoints",
    )
    api_secret: SecretStr | None = Field(
        default=None,
        description="API secret for signed endpoints",
    )

    # API Endpoints
    rest_base_url: str = Field(
        default="https://api.binance.th",
        description="REST API base URL",
    )
    ws_base_url_global: str = Field(
        default="wss://www.binance.th/gstream",
        description="WebSocket URL for GLOBAL symbols",
    )
    ws_base_url_site: str = Field(
        default="wss://www.binance.th/nstream",
        description="WebSocket URL for SITE symbols",
    )

    # Client Settings
    timeout: float = Field(
        default=30.0,
        description="Request timeout in seconds",
        gt=0,
    )
    max_retries: int = Field(
        default=3,
        description="Maximum retries for transient errors",
        ge=0,
    )
    enable_rate_limiting: bool = Field(
        default=True,
        description="Enable automatic rate limiting",
    )
    recv_window: int = Field(
        default=5000,
        description="Request validity window in milliseconds (max 60000)",
        gt=0,
        le=60000,
    )

    # WebSocket Settings
    ws_auto_reconnect: bool = Field(
        default=True,
        description="Enable automatic WebSocket reconnection",
    )
    ws_ping_interval: int = Field(
        default=20,
        description="WebSocket ping interval in seconds",
        gt=0,
    )
    ws_ping_timeout: int = Field(
        default=10,
        description="WebSocket ping timeout in seconds",
        gt=0,
    )

    # Logging Settings
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)",
    )
    log_requests: bool = Field(
        default=False,
        description="Log all API requests (for debugging)",
    )
    log_responses: bool = Field(
        default=False,
        description="Log all API responses (for debugging)",
    )

    def has_credentials(self) -> bool:
        """Check if API credentials are configured.

        Returns:
            True if both api_key and api_secret are set
        """
        return self.api_key is not None and self.api_secret is not None

    def get_secret_value(self) -> str | None:
        """Get the API secret value.

        Returns:
            The secret string or None if not configured
        """
        if self.api_secret is not None:
            return self.api_secret.get_secret_value()
        return None
