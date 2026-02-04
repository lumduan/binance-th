"""Pytest configuration and fixtures for Binance Thailand library tests."""

import pytest

from binance_th.config import BinanceThConfig


@pytest.fixture
def config() -> BinanceThConfig:
    """Create test configuration."""
    return BinanceThConfig(
        api_key="test_api_key",
        api_secret="test_api_secret",
    )


@pytest.fixture
def config_no_auth() -> BinanceThConfig:
    """Create test configuration without authentication."""
    return BinanceThConfig()
