"""Tests for secret redaction (ADR-0017)."""

from binance_th.redaction import REDACTED, redact_headers, redact_params, redact_query


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
