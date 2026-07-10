"""Tests for the listenKey lifecycle manager (ADR-0008)."""

import asyncio
from typing import Any

import httpx
import pytest

from binance_th.config import BinanceThConfig
from binance_th.exceptions import BinanceThAuthError
from binance_th.listenkey import RestListenKeyManager
from binance_th.models.enums import SymbolType

from .conftest import TransportFactory

_GLOBAL_KEY = "G" * 60
_SITE_KEY = "S" * 64  # 64 chars — the live SITE key length that the server keepalive regex rejects
_LIST = [
    {"listenKey": _GLOBAL_KEY, "type": "GLOBAL"},
    {"listenKey": _SITE_KEY, "type": "SITE"},
]


def _handler(request: httpx.Request) -> httpx.Response:
    """POST -> dual-key list; PUT/DELETE -> ok, except a >60-char key is rejected (server regex)."""
    assert request.url.path == "/api/v1/listenKey"
    if request.method == "POST":
        return httpx.Response(200, json=_LIST)
    key = request.url.params.get("listenKey", "")
    if len(key) > 60:
        return httpx.Response(400, json={"code": -1100, "msg": "Illegal characters"})
    return httpx.Response(200, json={})


async def _settle(pred: Any, *, steps: int = 500) -> None:
    for _ in range(steps):
        if pred():
            return
        await asyncio.sleep(0)
    raise AssertionError("condition not met")


class TestRestListenKeyManager:
    async def test_create_parses_dual_keys_api_key_only(
        self, mock_transport: TransportFactory
    ) -> None:
        cfg = BinanceThConfig(api_key="KEY")
        transport, captured = mock_transport(_handler, config=cfg)
        mgr = RestListenKeyManager(transport, cfg)
        await mgr.create()
        assert mgr.key_for(SymbolType.GLOBAL) == _GLOBAL_KEY
        assert mgr.key_for(SymbolType.SITE) == _SITE_KEY
        post = next(r for r in captured if r.method == "POST")
        assert post.headers.get("X-MBX-APIKEY") == "KEY"  # api-key header present
        assert b"signature" not in post.url.query  # but NOT signed
        await mgr.close()

    async def test_create_fail_fast_without_key(self, mock_transport: TransportFactory) -> None:
        cfg = BinanceThConfig()  # no api_key
        transport, captured = mock_transport(_handler, config=cfg)
        mgr = RestListenKeyManager(transport, cfg)
        with pytest.raises(BinanceThAuthError):
            await mgr.create()
        assert captured == []  # failed before any network hit

    async def test_keepalive_is_best_effort_per_key(self, mock_transport: TransportFactory) -> None:
        cfg = BinanceThConfig(api_key="KEY")
        transport, captured = mock_transport(_handler, config=cfg)
        mgr = RestListenKeyManager(transport, cfg)
        await mgr.create()
        # SITE key PUT is rejected by the server, but keepalive must not raise
        await mgr.keepalive()
        puts = [r for r in captured if r.method == "PUT"]
        assert {r.url.params["listenKey"] for r in puts} == {
            _GLOBAL_KEY,
            _SITE_KEY,
        }  # both attempted
        await mgr.close()

    async def test_keepalive_loop_fires_under_interval(
        self, mock_transport: TransportFactory
    ) -> None:
        recorded: list[float] = []

        async def fake_sleep(seconds: float) -> None:
            recorded.append(seconds)
            if len(recorded) >= 2:
                await asyncio.Event().wait()  # park after two ticks so the loop stops spinning

        cfg = BinanceThConfig(api_key="KEY")
        transport, captured = mock_transport(_handler, config=cfg)
        mgr = RestListenKeyManager(transport, cfg, sleep=fake_sleep, interval=900.0)
        await mgr.create()
        await _settle(lambda: any(r.method == "PUT" for r in captured))
        assert recorded[0] == 900.0
        assert recorded[0] < 1800.0  # the <30-min invariant
        await mgr.close()

    async def test_close_deletes_each_key_best_effort(
        self, mock_transport: TransportFactory
    ) -> None:
        cfg = BinanceThConfig(api_key="KEY")
        transport, captured = mock_transport(_handler, config=cfg)
        mgr = RestListenKeyManager(transport, cfg)
        await mgr.create()
        await mgr.close()
        deletes = [r for r in captured if r.method == "DELETE"]
        assert {r.url.params["listenKey"] for r in deletes} == {_GLOBAL_KEY, _SITE_KEY}
        assert mgr._keepalive_task is None
        await mgr.close()  # idempotent

    async def test_create_is_single_flight(self, mock_transport: TransportFactory) -> None:
        cfg = BinanceThConfig(api_key="KEY")
        transport, captured = mock_transport(_handler, config=cfg)
        mgr = RestListenKeyManager(transport, cfg)
        await asyncio.gather(mgr.create(), mgr.create())  # concurrent → one POST
        assert len([r for r in captured if r.method == "POST"]) == 1
        await mgr.close()
