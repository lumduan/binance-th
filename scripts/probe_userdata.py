#!/usr/bin/env python3
"""Throwaway credentialed user-data probe for Binance Thailand (M6).

**Read-only w.r.t. trading**: it POST/PUT/DELETEs a listenKey and connects the user-data
WebSocket to observe frames. It NEVER touches ``/api/v1/order`` — no order is placed, no
money moves. listenKey endpoints are API-KEY-only, so it needs only ``BINANCE_TH_API_KEY``
(no secret). The listenKey value is masked in all output.

It settles the M6 unknowns the ADRs never pin:
  (a) which user-data URL form actually streams (``{host}/ws/<key>`` vs ``?streams=<key>``
      vs a WSA-native SUBSCRIBE control frame), and which host;
  (b) the frame envelope (bare ``{"e":...}`` vs the market ``{"stream","data"}`` wrapper);
  (c) whether the listenKey response carries a GLOBAL/SITE ``type`` (⇒ maybe one key per type);
  (d) the keepalive PUT / DELETE param form, and any ``listenKeyExpired`` shape.

NOT shipped in the package (``scripts/`` is outside the hatchling build target).

Run (key inline, stays out of history):
    ! BINANCE_TH_API_KEY=<your-key> uv run python scripts/probe_userdata.py

=== VERIFIED FINDINGS (2026-07-10) — seed the M6 code to these ===
- POST /api/v1/listenKey (api-key-only) returns a LIST, one key per symbol type:
    [{"listenKey": "...", "type": "GLOBAL"}, {"listenKey": "...", "type": "SITE"}]
  (TH-specific; vanilla Binance returns a single key). POST is idempotent (same live keys).
- Connect URL (BOTH types): wss://nbstream.binance.th/w3w/wsa/stream/ws/<listenKey>
  (config.ws_base_url + "/ws/" + key). Market hosts are inconsistent (GLOBAL/gstream -> HTTP 502;
  SITE/nstream -> connects), so use the WSA host uniformly. No WSA-native session auth needed — the
  REST listenKey /ws/<key> form works, so the ADR-0008 WSA seam stays a (currently unused) fallback.
- keepalive PUT / close DELETE need ?listenKey=<key> (no-params & ?type= both -> -1102 mandatory).
  GLOBAL key (60 chars): PUT & DELETE -> OK. SITE key (64 chars): server REJECTS with
  -1100 "Illegal characters ... legal range ^[a-zA-Z0-9]{1,60}$" — the SITE key exceeds the server's
  own 60-char keepalive regex (a TH server bug). => SITE keys are NOT keepalive-able/deletable; they
  expire (~60 min) and the SITE connection self-heals by reconnecting with a fresh key. So keepalive
  and close are BEST-EFFORT per key (suppress per-key failures; never crash the manager).
- Frame envelope + event shapes: NOT observed (account was idle in-window) -> still ⚠ASSUMED
  bare {"e":...} + Binance-standard executionReport/outboundAccountPosition/balanceUpdate; verify in a
  later credentialed order-activity soak.
"""

from __future__ import annotations

import asyncio
import json
import time

from binance_th.config import BinanceThConfig
from binance_th.transport import Transport

try:
    from websockets.asyncio.client import connect
except ImportError:  # pragma: no cover
    raise SystemExit("websockets is required: `uv sync --extra dev`") from None

_LISTEN_KEY_PATH = "/api/v1/listenKey"
_WINDOW = 8.0


def _mask(secret: str) -> str:
    return secret if len(secret) < 10 else f"{secret[:4]}…{secret[-4:]}"


def _scrub(text: str, secret: str) -> str:
    return text.replace(secret, _mask(secret)) if secret else text


async def _observe(label: str, url: str, key: str, *, send: str | None = None) -> None:
    print(f"\n=== {label}\n    {_scrub(url, key)}")
    try:
        async with connect(url, ping_interval=20, ping_timeout=10) as ws:
            print("    -> connected")
            if send is not None:
                await ws.send(send)
                print(f"    -> sent: {_scrub(send, key)}")
            envelope: str | None = None
            seen: dict[str, list[str]] = {}
            deadline = time.monotonic() + _WINDOW
            count = 0
            while time.monotonic() < deadline and count < 30:
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=_WINDOW)
                except TimeoutError:
                    break
                count += 1
                try:
                    frame = json.loads(raw)
                except (ValueError, TypeError):
                    print(f"    -> non-json: {_scrub(str(raw)[:120], key)}")
                    continue
                if envelope is None:
                    wrapped = isinstance(frame, dict) and "stream" in frame and "data" in frame
                    envelope = "combined {stream,data}" if wrapped else "bare"
                    print(
                        f"    -> envelope: {envelope}  (first frame keys: "
                        f"{list(frame.keys()) if isinstance(frame, dict) else type(frame).__name__})"
                    )
                etype = frame.get("e") if isinstance(frame, dict) else None
                if isinstance(etype, str) and etype not in seen:
                    seen[etype] = list(frame.keys())
                    print(f"    -> event e={etype!r} keys={list(frame.keys())}")
                    print(f"       {_scrub(json.dumps(frame, ensure_ascii=False)[:400], key)}")
            if not seen:
                print(
                    "    -> (no typed events in window — expected if the account had no activity)"
                )
    except Exception as exc:  # probe: report and continue to the next candidate
        print(f"    -> FAILED: {type(exc).__name__}: {str(exc)[:160]}")


async def main() -> None:
    config = BinanceThConfig()  # reads BINANCE_TH_API_KEY from env/.env
    if config.api_key is None:
        raise SystemExit("set BINANCE_TH_API_KEY (api-key-only; no secret needed)")

    transport = Transport(config)
    keys: list[tuple[str, str]] = []  # (symbol_type, listenKey)
    try:
        # 1) POST listenKey — TH returns a LIST of {listenKey, type} (one per GLOBAL/SITE).
        raw = await transport.request("POST", _LISTEN_KEY_PATH, api_key_only=True, envelope=False)
        entries = raw if isinstance(raw, list) else [raw]
        for entry in entries:
            if isinstance(entry, dict) and entry.get("listenKey"):
                keys.append((str(entry.get("type", "?")), str(entry["listenKey"])))
        print(f"POST listenKey -> {len(entries)} entrie(s): {[(t, _mask(k)) for t, k in keys]}")
        if entries and isinstance(entries[0], dict):
            print(f"  per-entry keys: {list(entries[0].keys())}")
        if not keys:
            raise SystemExit("no listenKey in POST response")

        # 2) for each type's key, try the WSA host and the type's market host.
        base = config.ws_base_url
        for stype, key in keys:
            type_host = config.ws_base_url_global if stype == "GLOBAL" else config.ws_base_url_site
            await _observe(f"[{stype}] WSA /ws/<key>", f"{base}/ws/{key}", key)
            await _observe(f"[{stype}] WSA ?streams=<key>", f"{base}?streams={key}", key)
            await _observe(f"[{stype}] {stype}-host /ws/<key>", f"{type_host}/ws/{key}", key)

        # 3) keepalive PUT + 4) DELETE, per key (clean up)
        for stype, key in keys:
            for verb in ("PUT", "DELETE"):
                try:
                    await transport.request(
                        verb,
                        _LISTEN_KEY_PATH,
                        params={"listenKey": key},
                        api_key_only=True,
                        envelope=False,
                    )
                    print(f"{verb} [{stype}] (?listenKey=) -> ok")
                except Exception as exc:  # probe: report the outcome, don't abort
                    print(
                        f"{verb} [{stype}] (?listenKey=) -> {type(exc).__name__}: {str(exc)[:140]}"
                    )
    finally:
        await transport.aclose()

    print("\n=== NEXT: seed binance_th/models/userdata.py + the /ws URL to these findings ===")


if __name__ == "__main__":
    asyncio.run(main())
