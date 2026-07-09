"""Public async client entry point (ADR-0015).

:class:`BinanceThClient` owns the :class:`~binance_th.transport.Transport`
lifecycle behind an async context manager, so
``async with BinanceThClient(cfg) as client:`` opens and deterministically
closes the HTTP connection. M1 exposes the two general endpoints needed to
bootstrap everything else — :meth:`ping` and :meth:`server_time`; resource
clients (market, account, orders) arrive in M3.
"""

from types import TracebackType
from typing import Self

from binance_th.config import BinanceThConfig
from binance_th.models.base import ServerTime
from binance_th.transport import Transport

__all__ = ["BinanceThClient"]

PING_PATH = "/api/v1/ping"


class BinanceThClient:
    """Async client for the Binance Thailand API."""

    def __init__(
        self,
        config: BinanceThConfig | None = None,
        *,
        transport: Transport | None = None,
    ) -> None:
        """Build from ``config`` (or env/``.env`` defaults); ``transport`` is injectable for tests."""
        self._config = config or BinanceThConfig()
        self._transport = transport or Transport(self._config)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    @property
    def is_closed(self) -> bool:
        """True once the client has been closed."""
        return self._transport.is_closed

    async def aclose(self) -> None:
        """Close the underlying transport; idempotent."""
        await self._transport.aclose()

    async def ping(self) -> bool:
        """``GET /api/v1/ping`` — True if the API is reachable.

        The endpoint returns the non-JSON literal ``pong`` (verified 2026-07-09),
        so the body is read as text and never JSON-decoded.
        """
        text = await self._transport.request(
            "GET", PING_PATH, envelope=False, parse_json=False, weight=1
        )
        return isinstance(text, str) and text.strip() == "pong"

    async def server_time(self) -> ServerTime:
        """``GET /api/v1/time`` — server time; also refreshes the signing offset."""
        return await self._transport.sync_time()
