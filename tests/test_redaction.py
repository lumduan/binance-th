"""Tests for secret redaction (ADR-0017)."""

import logging

import httpx
import pytest

from binance_th.config import BinanceThConfig
from binance_th.redaction import REDACTED, redact_headers, redact_params, redact_query
from binance_th.timesync import TimeSync

from .conftest import TransportFactory


def _synced_ts(now: int = 1700000000000) -> TimeSync:
    ts = TimeSync(clock=lambda: now)
    ts.update(now)
    return ts


class TestRedactParams:
    """Tests for redact_params."""

    def test_masks_signature_and_secret(self) -> None:
        """Sensitive parameter values are replaced."""
        out = redact_params({"symbol": "BTCTHB", "signature": "abc", "api_secret": "s"})
        assert out["symbol"] == "BTCTHB"
        assert out["signature"] == REDACTED
        assert out["api_secret"] == REDACTED

    def test_case_insensitive_keys(self) -> None:
        """Key matching ignores case."""
        out = redact_params({"Signature": "abc", "API_SECRET": "s", "listenKey": "k"})
        assert out["Signature"] == REDACTED
        assert out["API_SECRET"] == REDACTED
        assert out["listenKey"] == REDACTED

    def test_non_sensitive_untouched(self) -> None:
        """Ordinary parameters pass through unchanged."""
        out = redact_params({"symbol": "BTCTHB", "quantity": "1"})
        assert out == {"symbol": "BTCTHB", "quantity": "1"}

    def test_deep_masks_nested_values(self) -> None:
        """Sensitive keys nested inside dicts/lists are masked at any depth."""
        out = redact_params(
            {
                "outer": {"listenKey": "k", "safe": "v"},
                "items": [{"token": "t"}, {"symbol": "BTCTHB"}],
            }
        )
        assert out["outer"]["listenKey"] == REDACTED
        assert out["outer"]["safe"] == "v"
        assert out["items"][0]["token"] == REDACTED
        assert out["items"][1]["symbol"] == "BTCTHB"


class TestNoSecretInLogs:
    """ADR-0017 falsifiable: enabled request/response logging leaks no credential value."""

    async def test_signed_call_logs_are_redacted(
        self, mock_transport: TransportFactory, caplog: pytest.LogCaptureFixture
    ) -> None:
        cfg = BinanceThConfig(
            api_key="KEY", api_secret="TOPSECRET", log_requests=True, log_responses=True
        )

        def handler(_request: httpx.Request) -> httpx.Response:
            # a response body carrying a listenKey (nested) that must be redacted
            return httpx.Response(200, json={"data": {"listenKey": "LEAKYKEY123"}, "ok": True})

        transport, captured = mock_transport(handler, config=cfg, timesync=_synced_ts())
        with caplog.at_level(logging.DEBUG, logger="binance_th"):
            await transport.request("GET", "/api/v1/account", signed=True, envelope=False)

        blob = caplog.text
        signature = captured[-1].url.params["signature"]
        assert REDACTED in blob  # redaction actually ran
        assert "TOPSECRET" not in blob  # api_secret never reaches a log
        assert "LEAKYKEY123" not in blob  # nested listenKey in the response body is masked
        assert signature not in blob  # the request signature is masked, not logged raw


class TestRedactHeaders:
    """Tests for redact_headers."""

    def test_masks_api_key_header(self) -> None:
        """The X-MBX-APIKEY header value is masked."""
        out = redact_headers({"X-MBX-APIKEY": "key123", "Content-Type": "application/json"})
        assert out["X-MBX-APIKEY"] == REDACTED
        assert out["Content-Type"] == "application/json"


class TestRedactQuery:
    """Tests for redact_query."""

    def test_masks_signature_value(self) -> None:
        """The signature value in a raw query string is masked."""
        out = redact_query("symbol=BTCTHB&timestamp=1&signature=deadbeef")
        assert f"signature={REDACTED}" in out
        assert "deadbeef" not in out
        assert "symbol=BTCTHB" in out

    def test_does_not_mask_substring_key(self) -> None:
        """A key that merely contains a sensitive word is not masked."""
        out = redact_query("mysignature=keepme&signature=x")
        assert "keepme" in out
        assert f"signature={REDACTED}" in out
