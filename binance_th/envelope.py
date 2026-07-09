"""Centralized response-envelope unwrapping (ADR-0002).

Binance TH wraps **signed** responses as ``{"code":0,"msg":...,"timestamp":...,
"data":...}`` where ``code == 0`` is success. Public market/system endpoints
return **bare** payloads (a raw object/array — verified 2026-07-09; ``/ping``
even returns non-JSON ``pong``). This module owns the single place that turns an
enveloped payload into its ``data`` and routes a non-zero ``code`` to a typed
error. Bare payloads never reach here — the caller passes ``envelope=False``.
"""

from typing import Any

from binance_th.errors import raise_envelope_error
from binance_th.exceptions import BinanceThValidationError

__all__ = ["is_envelope", "unwrap"]


def is_envelope(payload: Any) -> bool:
    """True if ``payload`` looks like the ``{code, msg, ...}`` response envelope."""
    return isinstance(payload, dict) and isinstance(payload.get("code"), int)


def unwrap(payload: Any, *, status_code: int, request_id: str | None = None) -> Any:
    """Return ``data`` from an envelope, raising on a non-zero ``code``.

    Raises:
        BinanceThAPIError: subclass, when the envelope ``code`` is non-zero.
        BinanceThValidationError: when an envelope was expected but the payload
            is not envelope-shaped (an endpoint mis-classified as enveloped).
    """
    if not is_envelope(payload):
        raise BinanceThValidationError(
            "Expected an enveloped response but received a bare payload",
            field="response",
            value=payload,
        )
    code = payload["code"]
    if code != 0:
        raise_envelope_error(
            code,
            str(payload.get("msg", "")),
            status_code=status_code,
            response_data=payload,
            request_id=request_id,
        )
    return payload.get("data")
