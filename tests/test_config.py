"""Tests for configuration management."""

import pytest
from pydantic import SecretStr

from binance_th.config import BinanceThConfig


class TestBinanceThConfig:
    """Tests for BinanceThConfig class."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = BinanceThConfig()
        assert config.api_key is None
        assert config.api_secret is None
        assert config.rest_base_url == "https://api.binance.th"
        assert config.ws_base_url_global == "wss://www.binance.th/gstream"
        assert config.ws_base_url_site == "wss://www.binance.th/nstream"
        assert config.timeout == 30.0
        assert config.max_retries == 3
        assert config.enable_rate_limiting is True
        assert config.recv_window == 5000
        assert config.ws_auto_reconnect is True
        assert config.ws_ping_interval == 20
        assert config.ws_ping_timeout == 10
        assert config.log_level == "INFO"
        assert config.log_requests is False
        assert config.log_responses is False

    def test_with_credentials(self) -> None:
        """Test configuration with API credentials."""
        config = BinanceThConfig(
            api_key="test_key",
            api_secret="test_secret",
        )
        assert config.api_key == "test_key"
        assert config.api_secret is not None
        assert isinstance(config.api_secret, SecretStr)
        assert config.api_secret.get_secret_value() == "test_secret"

    def test_has_credentials(self) -> None:
        """Test has_credentials method."""
        config_no_auth = BinanceThConfig()
        assert config_no_auth.has_credentials() is False

        config_with_key = BinanceThConfig(api_key="test")
        assert config_with_key.has_credentials() is False

        config_with_secret = BinanceThConfig(api_secret="test")
        assert config_with_secret.has_credentials() is False

        config_full = BinanceThConfig(api_key="key", api_secret="secret")
        assert config_full.has_credentials() is True

    def test_get_secret_value(self) -> None:
        """Test get_secret_value method."""
        config_no_auth = BinanceThConfig()
        assert config_no_auth.get_secret_value() is None

        config_with_secret = BinanceThConfig(api_key="key", api_secret="my_secret")
        assert config_with_secret.get_secret_value() == "my_secret"

    def test_recv_window_validation(self) -> None:
        """Test recvWindow validation."""
        # Valid values
        config = BinanceThConfig(recv_window=5000)
        assert config.recv_window == 5000

        config = BinanceThConfig(recv_window=60000)
        assert config.recv_window == 60000

        # Invalid values
        with pytest.raises(ValueError):
            BinanceThConfig(recv_window=0)

        with pytest.raises(ValueError):
            BinanceThConfig(recv_window=70000)

    def test_timeout_validation(self) -> None:
        """Test timeout validation."""
        config = BinanceThConfig(timeout=60.0)
        assert config.timeout == 60.0

        with pytest.raises(ValueError):
            BinanceThConfig(timeout=-1.0)

    def test_custom_urls(self) -> None:
        """Test custom URL configuration."""
        config = BinanceThConfig(
            rest_base_url="https://custom.api.com",
            ws_base_url_global="wss://custom.ws.com/global",
            ws_base_url_site="wss://custom.ws.com/site",
        )
        assert config.rest_base_url == "https://custom.api.com"
        assert config.ws_base_url_global == "wss://custom.ws.com/global"
        assert config.ws_base_url_site == "wss://custom.ws.com/site"

    def test_extra_fields_ignored(self) -> None:
        """Test that extra fields are ignored."""
        config = BinanceThConfig(
            api_key="test",
            unknown_field="should_be_ignored",  # type: ignore[call-arg]
        )
        assert config.api_key == "test"
        assert not hasattr(config, "unknown_field")
