"""Tests for the error taxonomy mapper (ADR-0006)."""

import pytest

from binance_th.errors import ENVELOPE_CODE_MAP, map_exception, raise_for_http_status
from binance_th.exceptions import (
    BinanceThAPIError,
    BinanceThAuthError,
    BinanceThBadRequestError,
    BinanceThIPBannedError,
    BinanceThRateLimitError,
    BinanceThServerError,
    BinanceThWAFError,
)


class TestMapException:
    """Tests for map_exception."""

    @pytest.mark.parametrize(
        ("status", "cls"),
        [
            (400, BinanceThBadRequestError),
            (401, BinanceThAuthError),
            (403, BinanceThWAFError),
            (418, BinanceThIPBannedError),
            (429, BinanceThRateLimitError),
            (500, BinanceThServerError),
            (503, BinanceThServerError),
        ],
    )
    def test_http_status_mapping(self, status: int, cls: type[BinanceThAPIError]) -> None:
        """HTTP status maps to the matching typed exception when no code is present."""
        assert map_exception(status, None) is cls

    def test_envelope_code_wins(self) -> None:
        """A non-zero envelope code takes precedence over the HTTP status."""
        assert map_exception(400, -1021) is BinanceThAuthError

    def test_unknown_code_defaults_to_api_error(self) -> None:
        """An unrecognized code, or no signal at all, falls back to the base API error."""
        assert map_exception(None, -99999) is BinanceThAPIError
        assert map_exception(None, None) is BinanceThAPIError

    def test_envelope_code_map_known_codes(self) -> None:
        """The map contains the load-bearing codes."""
        assert ENVELOPE_CODE_MAP[-1021] is BinanceThAuthError
        assert ENVELOPE_CODE_MAP[-1013] is BinanceThBadRequestError


class TestRaiseForHttpStatus:
    """Tests for raise_for_http_status."""

    def test_noop_for_2xx(self) -> None:
        """A 2xx status does not raise."""
        raise_for_http_status(200, {"serverTime": 1}, {})

    def test_raises_auth_on_401(self) -> None:
        """A 401 with an auth code raises BinanceThAuthError."""
        with pytest.raises(BinanceThAuthError):
            raise_for_http_status(401, {"code": -2015, "msg": "bad key"}, {})

    def test_rate_limit_extracts_headers(self) -> None:
        """A 429 captures Retry-After and used weight."""
        with pytest.raises(BinanceThRateLimitError) as exc:
            raise_for_http_status(
                429, {"msg": "too many"}, {"Retry-After": "5", "x-mbx-used-weight-1m": "6000"}
            )
        assert exc.value.retry_after == 5
        assert exc.value.used_weight == 6000

    def test_ip_banned_retry_after(self) -> None:
        """A 418 captures Retry-After on the IP-ban error."""
        with pytest.raises(BinanceThIPBannedError) as exc:
            raise_for_http_status(418, {}, {"Retry-After": "120"})
        assert exc.value.retry_after == 120

    def test_malformed_retry_after_ignored(self) -> None:
        """A non-numeric Retry-After is ignored rather than raising."""
        with pytest.raises(BinanceThRateLimitError) as exc:
            raise_for_http_status(429, {"msg": "x"}, {"Retry-After": "soon"})
        assert exc.value.retry_after is None

    def test_request_id_captured(self) -> None:
        """The request id header is attached to the exception."""
        with pytest.raises(BinanceThBadRequestError) as exc:
            raise_for_http_status(400, {"code": -1100, "msg": "bad"}, {"x-mbx-uuid": "req-1"})
        assert exc.value.request_id == "req-1"
