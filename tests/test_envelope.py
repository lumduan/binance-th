"""Tests for centralized envelope unwrapping (ADR-0002)."""

import pytest

from binance_th.envelope import is_envelope, unwrap
from binance_th.exceptions import BinanceThAuthError, BinanceThValidationError


class TestIsEnvelope:
    """Tests for is_envelope."""

    def test_true_for_envelope(self) -> None:
        """A {code, msg, data} dict is recognized as an envelope."""
        assert is_envelope({"code": 0, "msg": "", "data": {}}) is True

    def test_false_for_bare_or_non_dict(self) -> None:
        """Bare payloads and non-dicts are not envelopes."""
        assert is_envelope({"serverTime": 1}) is False
        assert is_envelope([1, 2, 3]) is False
        assert is_envelope("pong") is False


class TestUnwrap:
    """Tests for unwrap."""

    def test_returns_data_on_success(self) -> None:
        """code == 0 returns the data payload."""
        assert unwrap({"code": 0, "msg": "", "data": {"x": 1}}, status_code=200) == {"x": 1}

    def test_raises_on_nonzero_code(self) -> None:
        """A non-zero code raises the mapped typed exception."""
        with pytest.raises(BinanceThAuthError) as exc:
            unwrap({"code": -1021, "msg": "bad ts"}, status_code=200)
        assert exc.value.code == -1021

    def test_raises_validation_when_bare(self) -> None:
        """An envelope-expected but bare payload is a validation error."""
        with pytest.raises(BinanceThValidationError):
            unwrap({"serverTime": 1}, status_code=200)
