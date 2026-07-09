"""Tests for the async transport pipeline (ADR-0001/0002/0004/0006/0015)."""

import hashlib
import hmac
import logging

import httpx
import pytest

from binance_th.config import BinanceThConfig
from binance_th.exceptions import (
    BinanceThAuthError,
    BinanceThBadRequestError,
    BinanceThNetworkError,
    BinanceThRateLimitError,
    BinanceThServerError,
    BinanceThTimeoutError,
)
from binance_th.timesync import TimeSync

from .conftest import TransportFactory


def _json(
    payload: object, status: int = 200, headers: dict[str, str] | None = None
) -> httpx.Response:
    """Build a JSON response."""
    return httpx.Response(status, json=payload, headers=headers or {})


def _synced_ts(now: int = 1700000000000) -> TimeSync:
    """A TimeSync already synced with a fixed clock (offset 0)."""
    ts = TimeSync(clock=lambda: now)
    ts.update(now)
    return ts


class TestPublicRequests:
    """Bare (unsigned) public endpoints."""

    async def test_server_time_bare(self, mock_transport: TransportFactory) -> None:
        """sync_time parses a bare {serverTime} body and updates the offset."""

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/api/v1/time"
            return _json({"serverTime": 1700000000000})

        transport, captured = mock_transport(handler)
        server_time = await transport.sync_time()
        assert server_time.server_time == 1700000000000
        assert len(captured) == 1

    async def test_ping_non_json(self, mock_transport: TransportFactory) -> None:
        """A non-JSON `pong` body is returned as text, never JSON-decoded."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, text="pong")

        transport, _ = mock_transport(handler)
        result = await transport.request("GET", "/api/v1/ping", envelope=False, parse_json=False)
        assert result == "pong"


class TestSignedRequests:
    """Signed (enveloped) endpoints."""

    async def test_signed_account_happy(self, mock_transport: TransportFactory) -> None:
        """A signed request carries the api-key header and a correct trailing signature."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return _json({"code": 0, "msg": "", "data": {"balances": []}})

        cfg = BinanceThConfig(api_key="KEY", api_secret="SECRET")
        transport, captured = mock_transport(handler, config=cfg, timesync=_synced_ts())
        data = await transport.request("GET", "/api/v1/account", signed=True, weight=10)

        assert data == {"balances": []}
        request = captured[-1]
        assert request.headers["X-MBX-APIKEY"] == "KEY"
        query = request.url.query.decode()
        assert query.split("&")[-1].startswith("signature=")
        expected_sig = hmac.new(
            b"SECRET", b"recvWindow=5000&timestamp=1700000000000", hashlib.sha256
        ).hexdigest()
        assert f"signature={expected_sig}" in query

    async def test_signed_lazy_time_sync(self, mock_transport: TransportFactory) -> None:
        """An unsynced client fetches server time before its first signed call."""
        calls = {"time": 0, "account": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/api/v1/time":
                calls["time"] += 1
                return _json({"serverTime": 1700000000000})
            calls["account"] += 1
            return _json({"code": 0, "msg": "", "data": {}})

        cfg = BinanceThConfig(api_key="K", api_secret="S")
        transport, _ = mock_transport(handler, config=cfg)  # default unsynced TimeSync
        await transport.request("GET", "/api/v1/account", signed=True)
        assert calls == {"time": 1, "account": 1}

    async def test_signed_without_credentials_raises_locally(
        self, mock_transport: TransportFactory
    ) -> None:
        """A signed call without credentials fails before any network hit."""

        def handler(_request: httpx.Request) -> httpx.Response:  # pragma: no cover - never called
            return _json({"serverTime": 1})

        transport, captured = mock_transport(handler, config=BinanceThConfig())
        with pytest.raises(BinanceThAuthError):
            await transport.request("GET", "/api/v1/account", signed=True)
        assert captured == []

    async def test_api_key_only_sets_header(self, mock_transport: TransportFactory) -> None:
        """An api-key-only call sends the header without signing."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return _json({"listenKey": "abc"})

        cfg = BinanceThConfig(api_key="MYKEY", api_secret="S")
        transport, captured = mock_transport(handler, config=cfg)
        await transport.request("POST", "/api/v1/listenKey", api_key_only=True, envelope=False)
        assert captured[-1].headers["X-MBX-APIKEY"] == "MYKEY"
        assert b"signature" not in captured[-1].url.query


class TestTimestampResync:
    """The single -1021 resync (ADR-0004)."""

    async def test_resync_then_success(self, mock_transport: TransportFactory) -> None:
        """A -1021 triggers one time resync and a single retry that succeeds."""
        calls = {"time": 0, "account": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/api/v1/time":
                calls["time"] += 1
                return _json({"serverTime": 1700000000001})
            calls["account"] += 1
            if calls["account"] == 1:
                return _json({"code": -1021, "msg": "ts"}, status=400)
            return _json({"code": 0, "msg": "", "data": {"ok": True}})

        cfg = BinanceThConfig(api_key="K", api_secret="S")
        transport, _ = mock_transport(handler, config=cfg, timesync=_synced_ts())
        data = await transport.request("GET", "/api/v1/account", signed=True)
        assert data == {"ok": True}
        assert calls == {"time": 1, "account": 2}

    async def test_resync_persists_raises(self, mock_transport: TransportFactory) -> None:
        """A persistent -1021 raises after exactly one retry (no loop)."""
        calls = {"account": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/api/v1/time":
                return _json({"serverTime": 1700000000001})
            calls["account"] += 1
            return _json({"code": -1021, "msg": "ts"}, status=400)

        cfg = BinanceThConfig(api_key="K", api_secret="S")
        transport, _ = mock_transport(handler, config=cfg, timesync=_synced_ts())
        with pytest.raises(BinanceThAuthError) as exc:
            await transport.request("GET", "/api/v1/account", signed=True)
        assert exc.value.code == -1021
        assert calls["account"] == 2


class TestErrorMapping:
    """HTTP and envelope errors surface as typed exceptions."""

    async def test_http_401_raises_auth(self, mock_transport: TransportFactory) -> None:
        """A 401 raises BinanceThAuthError."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return _json({"code": -2015, "msg": "bad key"}, status=401)

        cfg = BinanceThConfig(api_key="K", api_secret="S")
        transport, _ = mock_transport(handler, config=cfg, timesync=_synced_ts())
        with pytest.raises(BinanceThAuthError):
            await transport.request("GET", "/api/v1/account", signed=True)

    async def test_http_429_extracts_headers(self, mock_transport: TransportFactory) -> None:
        """A 429 maps to a rate-limit error carrying Retry-After and weight."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                429,
                json={"msg": "slow"},
                headers={"Retry-After": "3", "x-mbx-used-weight-1m": "6000"},
            )

        transport, _ = mock_transport(handler)
        with pytest.raises(BinanceThRateLimitError) as exc:
            await transport.request("GET", "/api/v1/depth")
        assert exc.value.retry_after == 3
        assert exc.value.used_weight == 6000

    async def test_envelope_error_on_200(self, mock_transport: TransportFactory) -> None:
        """A 200 with a non-zero envelope code raises the mapped exception."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return _json({"code": -1100, "msg": "bad param"})

        cfg = BinanceThConfig(api_key="K", api_secret="S")
        transport, _ = mock_transport(handler, config=cfg, timesync=_synced_ts())
        with pytest.raises(BinanceThBadRequestError):
            await transport.request("GET", "/api/v1/account", signed=True)

    async def test_5xx_non_json_body(self, mock_transport: TransportFactory) -> None:
        """A 5xx with a non-JSON body still maps to a server error."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(503, text="Service Unavailable")

        transport, _ = mock_transport(handler)
        with pytest.raises(BinanceThServerError):
            await transport.request("GET", "/api/v1/time", envelope=False)

    async def test_timeout_mapped(self, mock_transport: TransportFactory) -> None:
        """An httpx timeout maps to BinanceThTimeoutError."""

        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout("timed out", request=request)

        transport, _ = mock_transport(handler)
        with pytest.raises(BinanceThTimeoutError):
            await transport.request("GET", "/api/v1/ping", envelope=False, parse_json=False)

    async def test_network_error_mapped(self, mock_transport: TransportFactory) -> None:
        """An httpx connection error maps to BinanceThNetworkError."""

        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("no route", request=request)

        transport, _ = mock_transport(handler)
        with pytest.raises(BinanceThNetworkError):
            await transport.request("GET", "/api/v1/time", envelope=False)

    async def test_is_retryable_predicate(self, mock_transport: TransportFactory) -> None:
        """Transient failures are retryable; auth failures are not (M2 seam)."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, text="pong")

        transport, _ = mock_transport(handler)
        assert transport._is_retryable(BinanceThNetworkError()) is True
        assert transport._is_retryable(BinanceThAuthError()) is False


class TestRedactionLogging:
    """Debug logging never leaks credentials (ADR-0017)."""

    async def test_no_secret_in_logs(
        self, mock_transport: TransportFactory, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Signature, api-key, and listenKey are redacted from request/response logs."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return _json({"code": 0, "msg": "", "data": {"listenKey": "SECRETKEY"}})

        cfg = BinanceThConfig(
            api_key="SUPERKEYVALUE",
            api_secret="TOPSECRET",
            log_requests=True,
            log_responses=True,
        )
        transport, _ = mock_transport(handler, config=cfg, timesync=_synced_ts())
        with caplog.at_level(logging.DEBUG, logger="binance_th"):
            await transport.request("GET", "/api/v1/account", signed=True)

        # The api-key/secret/listenKey *values* must not appear; the header *name*
        # X-MBX-APIKEY may (only its value is redacted).
        assert "TOPSECRET" not in caplog.text
        assert "SUPERKEYVALUE" not in caplog.text
        assert "SECRETKEY" not in caplog.text
        assert "***REDACTED***" in caplog.text

    async def test_logs_non_dict_response(
        self, mock_transport: TransportFactory, caplog: pytest.LogCaptureFixture
    ) -> None:
        """A non-dict (text) response body is logged as-is."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, text="pong")

        cfg = BinanceThConfig(log_requests=True, log_responses=True)
        transport, _ = mock_transport(handler, config=cfg)
        with caplog.at_level(logging.DEBUG, logger="binance_th"):
            await transport.request("GET", "/api/v1/ping", envelope=False, parse_json=False)
        assert "pong" in caplog.text
