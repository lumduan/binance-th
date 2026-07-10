#!/usr/bin/env python3
"""Throwaway live WebSocket probe for Binance Thailand (M5, WBS-M5-02).

Read-only, no credentials. Connects to candidate WebSocket URLs, subscribes to a
handful of public market streams for one SITE symbol (BTCTHB) and one GLOBAL
symbol (BTCUSDT), and prints the real frame shapes so the M5 decode models can be
built against verified data instead of ADR assumptions.

It settles the four things the ADRs never pin:
  (a) which URL/topology actually streams (single-host `?streams=` vs /gstream + /nstream),
  (b) the per-stream name suffixes (@depth / @trade / @kline_1m / @bookTicker / ...),
  (c) the combined-stream inbound envelope (assumed {"stream": ..., "data": ...}),
  (d) whether depthUpdate carries `pu` (previous-final-update-id).

NOT shipped in the package (scripts/ is outside the hatchling build target).

Run:  uv run python scripts/probe_ws.py

=== VERIFIED FINDINGS (2026-07-09) — seed the M5 models to these ===
Topology (FLIPPED vs ADR-0014 assumption): the single-host `nbstream…/w3w/wsa/stream` connects and
ACKs SUBSCRIBE but pushes NO market data (WSA request/response host). The working market-stream
topology is DUAL-HOST with a combined `{"stream": ..., "data": ...}` envelope:
  GLOBAL symbols -> wss://www.binance.th/gstream      SITE symbols -> wss://www.binance.th/nstream
GLOBAL/SITE payloads differ (ADR-0011 no-parity), so optional-mark the type-specific keys:
  depthUpdate  GLOBAL {e,E,s,U,u,b,a}          SITE {e,E,T,s,U,u,pu,b,a}   -> T, pu optional
  trade        GLOBAL {e,E,s,t,p,q,T,m,M}      SITE {e,E,T,s,t,p,q,m}      -> M optional
  aggTrade     GLOBAL {e,E,s,a,p,q,f,l,T,m,M}  SITE {e,E,a,s,p,q,f,l,T,m}  -> M optional
  bookTicker   GLOBAL {u,s,b,B,a,A}            SITE {u,e,s,b,B,a,A,T,E}    -> e, E, T optional
  ticker(e=24hrTicker) {e,E,s,p,P,w,x,c,Q,b,B,a,A,o,h,l,v,q,O,C,F,L,n}
  kline (e=kline) {e,E,s,k}, k={t,T,s,i,f,L,o,c,h,l,v,n,x,q,V,Q,B}  (identical GLOBAL/SITE)
b/a levels are [price, qty] string arrays (reuse OrderBookEntry.from_list).
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any

try:
    from websockets.asyncio.client import connect
except ImportError:  # pragma: no cover
    raise SystemExit(
        "websockets is required: `uv sync --extra dev` (or pip install websockets)"
    ) from None

# Candidate topologies to try, in preference order. Each entry:
#   (label, base_url, [symbols])
CANDIDATES: list[tuple[str, str, list[str]]] = [
    (
        "single-host (ADR-0014 default)",
        "wss://nbstream.binance.th/w3w/wsa/stream",
        ["btcthb", "btcusdt"],
    ),
    ("dual-host GLOBAL (/gstream)", "wss://www.binance.th/gstream", ["btcusdt"]),
    ("dual-host SITE (/nstream)", "wss://www.binance.th/nstream", ["btcthb"]),
]

# Stream-name suffixes to probe (Binance-style vocabulary — the probe confirms which exist).
CHANNELS = ["depth", "trade", "aggTrade", "kline_1m", "bookTicker", "ticker"]

FRAME_BUDGET = 25  # stop after this many frames per URL
TIME_BUDGET = 10.0  # ...or this many seconds, whichever first
RECV_TIMEOUT = 6.0  # per-recv timeout


def _streams_for(symbol: str) -> list[str]:
    return [f"{symbol}@{ch}" for ch in CHANNELS]


def _combined_url(base: str, symbols: list[str]) -> str:
    streams = [s for sym in symbols for s in _streams_for(sym)]
    return f"{base}?streams={'/'.join(streams)}"


def _classify(frame: Any) -> tuple[str, dict[str, Any]]:
    """Return (stream_name_or_event, payload) and whether it's the combined envelope."""
    if isinstance(frame, dict) and "stream" in frame and "data" in frame:
        return str(frame["stream"]), frame["data"]
    # Bare payload — infer a label from the event type if present.
    if isinstance(frame, dict):
        label = str(frame.get("e", frame.get("stream", "<bare>")))
        return label, frame
    return "<non-dict>", {"raw": frame}


async def _probe_url(label: str, url: str) -> dict[str, Any]:
    print(f"\n{'=' * 70}\nTRY  {label}\n     {url[:110]}{'...' if len(url) > 110 else ''}")
    findings: dict[str, Any] = {
        "label": label,
        "url": url,
        "connected": False,
        "envelope": None,  # "combined {stream,data}" | "bare"
        "samples": {},  # stream/event -> first raw payload
        "error": None,
    }
    try:
        async with connect(url, ping_interval=20, ping_timeout=10) as ws:
            findings["connected"] = True
            print("     -> connected")
            deadline = time.monotonic() + TIME_BUDGET
            count = 0
            while count < FRAME_BUDGET and time.monotonic() < deadline:
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=RECV_TIMEOUT)
                except TimeoutError:
                    print("     -> recv timeout (no more frames)")
                    break
                count += 1
                try:
                    frame = json.loads(raw)
                except (ValueError, TypeError):
                    print(f"     -> non-JSON frame: {raw!r:.120}")
                    continue
                if findings["envelope"] is None:
                    findings["envelope"] = (
                        "combined {stream,data}"
                        if isinstance(frame, dict) and "stream" in frame and "data" in frame
                        else "bare"
                    )
                name, payload = _classify(frame)
                if name not in findings["samples"]:
                    findings["samples"][name] = payload
                    keys = list(payload.keys()) if isinstance(payload, dict) else "<non-dict>"
                    print(f"     -> [{name}] keys={keys}")

            # Dynamic-subscribe probe on the open socket.
            if findings["connected"]:
                await _probe_dynamic_subscribe(ws, findings)
    except Exception as exc:  # probe: report any failure and keep trying the next candidate
        findings["error"] = f"{type(exc).__name__}: {exc}"
        print(f"     -> FAILED: {findings['error']}")
    return findings


async def _probe_dynamic_subscribe(ws: Any, findings: dict[str, Any]) -> None:
    """Send a SUBSCRIBE control frame and see whether the server acks it."""
    req = {"method": "SUBSCRIBE", "params": ["btcthb@aggTrade"], "id": 99}
    try:
        await ws.send(json.dumps(req))
        raw = await asyncio.wait_for(ws.recv(), timeout=RECV_TIMEOUT)
        frame = json.loads(raw)
        acked = isinstance(frame, dict) and frame.get("id") == 99
        findings["live_subscribe_ack"] = acked
        print(
            f"     -> dynamic SUBSCRIBE ack: {acked} ({frame if acked else 'first frame was data'})"
        )
    except (TimeoutError, ValueError, TypeError) as exc:
        findings["live_subscribe_ack"] = f"inconclusive: {type(exc).__name__}"
        print(f"     -> dynamic SUBSCRIBE inconclusive: {type(exc).__name__}")


def _print_findings(results: list[dict[str, Any]]) -> None:
    print(f"\n{'=' * 70}\n=== FINDINGS ===\n{'=' * 70}")
    working = [r for r in results if r["connected"] and r["samples"]]
    for r in results:
        status = (
            "OK"
            if (r["connected"] and r["samples"])
            else ("connected/no-data" if r["connected"] else "FAIL")
        )
        print(f"\n[{status}] {r['label']}")
        print(f"    url:      {r['url']}")
        print(f"    envelope: {r['envelope']}")
        if r.get("error"):
            print(f"    error:    {r['error']}")
        if "live_subscribe_ack" in r:
            print(f"    live SUBSCRIBE ack: {r['live_subscribe_ack']}")
        for name, payload in r["samples"].items():
            print(f"    stream {name}:")
            print(f"        {json.dumps(payload, ensure_ascii=False)[:400]}")

    print(f"\n{'-' * 70}")
    if not working:
        print(
            "NO URL STREAMED DATA — none of the candidates worked. Check network egress / URL forms."
        )
        return
    best = working[0]
    print(f"WORKING URL:          {best['url'].split('?')[0]}")
    print(f"ENVELOPE:             {best['envelope']}")
    depth_keys = None
    for name, payload in best["samples"].items():
        if "depth" in name.lower() or (
            isinstance(payload, dict) and payload.get("e") == "depthUpdate"
        ):
            depth_keys = list(payload.keys()) if isinstance(payload, dict) else None
    print(f"depthUpdate keys:     {depth_keys}")
    print(f"depthUpdate has `pu`: {('pu' in depth_keys) if depth_keys else 'unknown'}")
    print(f"stream names seen:    {sorted({n for r in working for n in r['samples']})}")
    print("\nNEXT: seed binance_th/models/stream.py to these shapes; stamp ADR-0014/0015 verified.")


async def main() -> None:
    results: list[dict[str, Any]] = []
    for label, base, symbols in CANDIDATES:
        results.append(await _probe_url(label, _combined_url(base, symbols)))
    _print_findings(results)


if __name__ == "__main__":
    asyncio.run(main())
