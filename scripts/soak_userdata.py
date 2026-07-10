#!/usr/bin/env python3
"""Guarded, opt-in user-data ORDER soak for Binance Thailand (M7).

⚠ **THIS PLACES A REAL ORDER — REAL MONEY.** It verifies the M6 user-data event shapes
(``executionReport``) that stayed ⚠ASSUMED because the probe account was idle. It places
**one tiny LIMIT BUY priced far below market** (so it rests and will not fill), captures the
resulting ``executionReport`` frames off ``client.user_stream``, then **cancels** it — so it
observes the NEW + CANCELED reports with minimal exposure (only the notional is briefly
reserved). Signatures/secrets/listenKeys are never printed.

Double-gated — refuses to run unless BOTH are set:
  BINANCE_TH_SOAK=1                                (explicit opt-in)
  BINANCE_TH_API_KEY + BINANCE_TH_API_SECRET       (signed; placing/cancelling an order)

Run:  BINANCE_TH_SOAK=1 uv run python scripts/soak_userdata.py
Optional:  BINANCE_TH_SOAK_SYMBOL=BTCTHB (default)

NOT shipped in the package (scripts/ is outside the hatchling build target).
"""

from __future__ import annotations

import asyncio
import json
import os
from decimal import ROUND_UP, Decimal
from typing import Any

from binance_th import BinanceThClient, BinanceThConfig, OrderSide, OrderType, TimeInForce
from binance_th.models.enums import FilterType
from binance_th.redaction import redact_params
from binance_th.validation import snap_price, snap_qty

_CAPTURE_SECONDS = 3.0


def _round_up(value: Decimal, step: Decimal | None) -> Decimal:
    if not step:
        return value
    return (value / step).to_integral_value(rounding=ROUND_UP) * step


def _dump(event: Any) -> str:
    """Masked JSON of an event's fields + any unmodelled extras (the real shape)."""
    body = redact_params(event.model_dump(by_alias=True))
    extra = list(event.model_extra or {})
    return json.dumps({"fields": body, "unmodelled_extra_keys": extra}, default=str)[:600]


async def main() -> None:
    if os.environ.get("BINANCE_TH_SOAK") != "1":
        raise SystemExit("refusing: set BINANCE_TH_SOAK=1 to run the REAL-ORDER soak")
    config = BinanceThConfig()
    if not config.has_credentials():
        raise SystemExit("refusing: needs BINANCE_TH_API_KEY + BINANCE_TH_API_SECRET (signed)")
    symbol = os.environ.get("BINANCE_TH_SOAK_SYMBOL", "BTCTHB")

    async with BinanceThClient(config) as client:
        # 1) size a valid but far-from-market resting LIMIT BUY
        book = await client.market.depth(symbol, limit=5)
        if not book.bids:
            raise SystemExit(f"no bids for {symbol}")
        best_bid = book.bids[0].price
        info = await client.exchange_info()
        sym = info.get_symbol(symbol)
        if sym is None:
            raise SystemExit(f"unknown symbol {symbol}")
        price_filter = sym.get_filter(FilterType.PRICE_FILTER)
        lot_filter = sym.get_filter(FilterType.LOT_SIZE)
        notional_filter = sym.get_filter(FilterType.MIN_NOTIONAL)

        tick = price_filter.tick_size if price_filter else None
        step = lot_filter.step_size if lot_filter else None
        min_notional = (notional_filter.min_notional if notional_filter else None) or Decimal("0")

        price = snap_price(best_bid * Decimal("0.5"), tick)  # ~50% below market -> will not fill
        # smallest qty that clears minNotional at that price (with a small margin)
        target = (min_notional * Decimal("1.05")) / price if price > 0 else Decimal("0")
        quantity = _round_up(target, step)
        if lot_filter and lot_filter.min_qty and quantity < lot_filter.min_qty:
            quantity = snap_qty(lot_filter.min_qty, step)
        print(f"symbol={symbol} best_bid={best_bid} -> resting price={price} qty={quantity}")

        # 2) start capturing order events BEFORE placing
        events: list[Any] = []

        async def _collect() -> None:
            async for event in client.user_stream.watch_orders():
                events.append(event)

        collector = asyncio.create_task(_collect())
        await asyncio.sleep(1.0)  # let the user-data socket connect

        # 3) place the resting order, capture NEW
        order = await client.orders.create_order(
            symbol,
            OrderSide.BUY,
            OrderType.LIMIT,
            quantity=quantity,
            price=price,
            time_in_force=TimeInForce.GTC,
        )
        print(f"placed order_id={order.order_id} status={order.status}")
        await asyncio.sleep(_CAPTURE_SECONDS)

        # 4) cancel, capture CANCELED
        try:
            await client.orders.cancel_order(symbol, order_id=order.order_id)
            print(f"cancelled order_id={order.order_id}")
        finally:
            await asyncio.sleep(_CAPTURE_SECONDS)
            collector.cancel()

        # 5) report the captured real shapes (masked)
        print(f"\n=== captured {len(events)} executionReport event(s) ===")
        for event in events:
            print(_dump(event))
        print(
            "\nNEXT: reconcile binance_th/models/userdata.py with any unmodelled_extra_keys above."
        )


if __name__ == "__main__":
    asyncio.run(main())
