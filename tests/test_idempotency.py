"""Tests for client-order-id minting (ADR-0013)."""

import re

from binance_th.idempotency import mint_client_order_id

_URL_SAFE = re.compile(r"^[A-Za-z0-9_-]{1,36}$")


class TestMintClientOrderId:
    """The minter is URL-safe, bounded, and unique."""

    def test_format_prefix_and_length(self) -> None:
        cid = mint_client_order_id()
        assert _URL_SAFE.match(cid)
        assert cid.startswith("xTHPY")
        assert len(cid) <= 36

    def test_deterministic_with_injection(self) -> None:
        assert mint_client_order_id("p", now_ms=lambda: 0, token=lambda: "abc") == "p-0-abc"

    def test_base36_of_time(self) -> None:
        # 36 (base10) -> "10" (base36)
        assert mint_client_order_id("p", now_ms=lambda: 36, token=lambda: "z") == "p-10-z"

    def test_unique_across_calls(self) -> None:
        ids = {mint_client_order_id() for _ in range(1000)}
        assert len(ids) == 1000

    def test_caps_at_max_len(self) -> None:
        cid = mint_client_order_id("P" * 50, now_ms=lambda: 1, token=lambda: "t")
        assert len(cid) == 36
