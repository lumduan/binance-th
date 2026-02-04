"""Tests for exception hierarchy."""

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
    get_exception_for_status_code,
)


class TestBinanceThError:
    """Tests for base BinanceThError class."""

    def test_basic_creation(self) -> None:
        """Test basic error creation."""
        error = BinanceThError("Test error")
        assert error.message == "Test error"
        assert error.code is None
        assert error.details == {}

    def test_with_code(self) -> None:
        """Test error with code."""
        error = BinanceThError("Test error", code=123)
        assert error.code == 123

    def test_with_details(self) -> None:
        """Test error with details."""
        details = {"key": "value"}
        error = BinanceThError("Test error", details=details)
        assert error.details == {"key": "value"}

    def test_str_without_code(self) -> None:
        """Test string representation without code."""
        error = BinanceThError("Test error")
        assert str(error) == "Test error"

    def test_str_with_code(self) -> None:
        """Test string representation with code."""
        error = BinanceThError("Test error", code=123)
        assert str(error) == "[123] Test error"

    def test_inheritance(self) -> None:
        """Test that it inherits from Exception."""
        error = BinanceThError("Test")
        assert isinstance(error, Exception)


class TestBinanceThAPIError:
    """Tests for BinanceThAPIError class."""

    def test_basic_creation(self) -> None:
        """Test basic API error creation."""
        error = BinanceThAPIError("API error")
        assert error.message == "API error"
        assert error.status_code is None
        assert error.request_id is None
        assert error.response_data == {}

    def test_with_all_params(self) -> None:
        """Test API error with all parameters."""
        error = BinanceThAPIError(
            message="API error",
            code=123,
            status_code=400,
            request_id="req-123",
            response_data={"error": "details"},
        )
        assert error.code == 123
        assert error.status_code == 400
        assert error.request_id == "req-123"
        assert error.response_data == {"error": "details"}

    def test_inheritance(self) -> None:
        """Test inheritance chain."""
        error = BinanceThAPIError("Test")
        assert isinstance(error, BinanceThError)
        assert isinstance(error, Exception)


class TestBinanceThRateLimitError:
    """Tests for BinanceThRateLimitError class."""

    def test_default_status_code(self) -> None:
        """Test default status code is 429."""
        error = BinanceThRateLimitError()
        assert error.status_code == 429

    def test_with_retry_after(self) -> None:
        """Test with retry_after parameter."""
        error = BinanceThRateLimitError(retry_after=60)
        assert error.retry_after == 60

    def test_with_weight_info(self) -> None:
        """Test with weight information."""
        error = BinanceThRateLimitError(
            used_weight=1200,
            limit_weight=1200,
        )
        assert error.used_weight == 1200
        assert error.limit_weight == 1200

    def test_inheritance(self) -> None:
        """Test inheritance chain."""
        error = BinanceThRateLimitError()
        assert isinstance(error, BinanceThAPIError)
        assert isinstance(error, BinanceThError)


class TestBinanceThIPBannedError:
    """Tests for BinanceThIPBannedError class."""

    def test_default_status_code(self) -> None:
        """Test default status code is 418."""
        error = BinanceThIPBannedError()
        assert error.status_code == 418

    def test_with_retry_after(self) -> None:
        """Test with retry_after parameter."""
        error = BinanceThIPBannedError(retry_after=120)
        assert error.retry_after == 120

    def test_default_message(self) -> None:
        """Test default message."""
        error = BinanceThIPBannedError()
        assert "auto-banned" in error.message


class TestBinanceThWAFError:
    """Tests for BinanceThWAFError class."""

    def test_default_status_code(self) -> None:
        """Test default status code is 403."""
        error = BinanceThWAFError()
        assert error.status_code == 403

    def test_default_message(self) -> None:
        """Test default message."""
        error = BinanceThWAFError()
        assert "WAF" in error.message


class TestBinanceThAuthError:
    """Tests for BinanceThAuthError class."""

    def test_default_status_code(self) -> None:
        """Test default status code is 401."""
        error = BinanceThAuthError()
        assert error.status_code == 401

    def test_inheritance(self) -> None:
        """Test inheritance chain."""
        error = BinanceThAuthError()
        assert isinstance(error, BinanceThAPIError)


class TestBinanceThBadRequestError:
    """Tests for BinanceThBadRequestError class."""

    def test_default_status_code(self) -> None:
        """Test default status code is 400."""
        error = BinanceThBadRequestError()
        assert error.status_code == 400


class TestBinanceThServerError:
    """Tests for BinanceThServerError class."""

    def test_default_message(self) -> None:
        """Test default message mentions unknown status."""
        error = BinanceThServerError()
        assert "unknown" in error.message.lower()


class TestBinanceThNetworkError:
    """Tests for BinanceThNetworkError class."""

    def test_inheritance(self) -> None:
        """Test inheritance - directly from BinanceThError."""
        error = BinanceThNetworkError()
        assert isinstance(error, BinanceThError)
        assert not isinstance(error, BinanceThAPIError)


class TestBinanceThTimeoutError:
    """Tests for BinanceThTimeoutError class."""

    def test_with_timeout(self) -> None:
        """Test with timeout value."""
        error = BinanceThTimeoutError(timeout=30.0)
        assert error.timeout == 30.0


class TestBinanceThValidationError:
    """Tests for BinanceThValidationError class."""

    def test_with_field_and_value(self) -> None:
        """Test with field and value."""
        error = BinanceThValidationError(
            message="Invalid value",
            field="quantity",
            value=-1,
        )
        assert error.field == "quantity"
        assert error.value == -1


class TestBinanceThWebSocketError:
    """Tests for BinanceThWebSocketError class."""

    def test_inheritance(self) -> None:
        """Test inheritance - directly from BinanceThError."""
        error = BinanceThWebSocketError()
        assert isinstance(error, BinanceThError)
        assert not isinstance(error, BinanceThAPIError)


class TestGetExceptionForStatusCode:
    """Tests for get_exception_for_status_code function."""

    def test_400_returns_bad_request(self) -> None:
        """Test 400 returns BinanceThBadRequestError."""
        assert get_exception_for_status_code(400) == BinanceThBadRequestError

    def test_401_returns_auth(self) -> None:
        """Test 401 returns BinanceThAuthError."""
        assert get_exception_for_status_code(401) == BinanceThAuthError

    def test_403_returns_waf(self) -> None:
        """Test 403 returns BinanceThWAFError."""
        assert get_exception_for_status_code(403) == BinanceThWAFError

    def test_418_returns_ip_banned(self) -> None:
        """Test 418 returns BinanceThIPBannedError."""
        assert get_exception_for_status_code(418) == BinanceThIPBannedError

    def test_429_returns_rate_limit(self) -> None:
        """Test 429 returns BinanceThRateLimitError."""
        assert get_exception_for_status_code(429) == BinanceThRateLimitError

    def test_5xx_returns_server_error(self) -> None:
        """Test 5xx returns BinanceThServerError."""
        assert get_exception_for_status_code(500) == BinanceThServerError
        assert get_exception_for_status_code(502) == BinanceThServerError
        assert get_exception_for_status_code(503) == BinanceThServerError
        assert get_exception_for_status_code(504) == BinanceThServerError
        assert get_exception_for_status_code(599) == BinanceThServerError

    def test_unknown_returns_api_error(self) -> None:
        """Test unknown status returns BinanceThAPIError."""
        assert get_exception_for_status_code(404) == BinanceThAPIError
        assert get_exception_for_status_code(422) == BinanceThAPIError
