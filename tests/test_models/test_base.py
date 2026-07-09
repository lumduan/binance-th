"""Tests for base / exchangeInfo models (M3a reconciliation to the live TH shape)."""

from binance_th.models.base import ExchangeInfo, SymbolInfo
from binance_th.models.enums import FilterType, SymbolType

# Trimmed real BNBTHB (SITE) symbol from live GET /api/v1/exchangeInfo (2026-07-09).
_LIVE_SYMBOL = {
    "symbol": "BNBTHB",
    "test": 0,
    "status": "TRADING",
    "baseAsset": "BNB",
    "baseAssetPrecision": 8,
    "quoteAsset": "THB",
    "quotePrecision": 6,
    "quoteAssetPrecision": 8,
    "baseCommissionPrecision": 2,
    "quoteCommissionPrecision": 0,
    "type": "SITE",
    "filters": [
        {
            "filterType": "PRICE_FILTER",
            "minPrice": "0.01",
            "maxPrice": "1000000.0",
            "tickSize": "0.01",
        }
    ],
    "orderTypes": ["LIMIT", "MARKET"],
}


class TestSymbolInfo:
    """The reconciled SymbolInfo parses the live TH shape (wbs gap #10)."""

    def test_parses_live_th_shape(self) -> None:
        """Added fields populate; global-only fields absent on TH default to None."""
        info = SymbolInfo(**_LIVE_SYMBOL)
        assert info.symbol == "BNBTHB"
        assert info.symbol_type == SymbolType.SITE
        assert info.test == 0
        assert info.base_commission_precision == 2
        assert info.quote_commission_precision == 0
        assert info.oco_allowed is None
        assert info.iceberg_allowed is None
        assert info.is_spot_trading_allowed is None
        assert info.is_margin_trading_allowed is None
        assert info.permissions is None

    def test_get_filter(self) -> None:
        """get_filter finds present filters and returns None for absent ones."""
        info = SymbolInfo(**_LIVE_SYMBOL)
        assert info.get_filter(FilterType.PRICE_FILTER) is not None
        assert info.get_filter(FilterType.LOT_SIZE) is None


class TestExchangeInfo:
    """ExchangeInfo(**live) no longer raises (the M1-discovered bug)."""

    def test_parses_live_th_shape(self) -> None:
        raw = {
            "timezone": "UTC",
            "serverTime": 1700000000000,
            "rateLimits": [
                {
                    "rateLimitType": "REQUEST_WEIGHT",
                    "interval": "MINUTE",
                    "intervalNum": 1,
                    "limit": 6000,
                }
            ],
            "exchangeFilters": [],
            "symbols": [_LIVE_SYMBOL],
        }
        info = ExchangeInfo(**raw)
        assert len(info.symbols) == 1
        symbol = info.get_symbol("BNBTHB")
        assert symbol is not None
        assert symbol.symbol_type == SymbolType.SITE
        assert info.rate_limits[0].limit == 6000
