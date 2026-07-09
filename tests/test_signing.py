"""Tests for HMAC request signing (ADR-0003)."""

import hashlib
import hmac

from pydantic import SecretStr

from binance_th.signing import Signer, build_query, sign_payload


class TestBuildQuery:
    """Tests for build_query."""

    def test_insertion_order_preserved(self) -> None:
        """Params are joined in insertion order, not sorted."""
        assert build_query({"b": "2", "a": "1", "c": "3"}) == "b=2&a=1&c=3"

    def test_excludes_signature(self) -> None:
        """A signature key is never part of the signed string."""
        assert build_query({"a": "1", "signature": "x"}) == "a=1"


class TestSignPayload:
    """Tests for sign_payload."""

    def test_matches_hmac_sha256(self) -> None:
        """The digest is a standard lowercase-hex HMAC-SHA256."""
        expected = hmac.new(b"secret", b"a=1", hashlib.sha256).hexdigest()
        assert sign_payload("secret", "a=1") == expected


class TestSigner:
    """Tests for the Signer."""

    def test_golden_vector(self) -> None:
        """Known params + secret produce a known signature (self-consistent vector)."""
        signer = Signer(SecretStr("mysecret"))
        params = signer.signed_params({"symbol": "BTCTHB", "side": "BUY"}, timestamp=1700000000000)
        payload = "symbol=BTCTHB&side=BUY&timestamp=1700000000000"
        expected = hmac.new(b"mysecret", payload.encode(), hashlib.sha256).hexdigest()
        assert params["signature"] == expected
        assert params["timestamp"] == "1700000000000"

    def test_signature_is_last_key(self) -> None:
        """The signature is always the final parameter."""
        params = Signer(SecretStr("s")).signed_params({"a": "1"}, timestamp=1)
        assert list(params)[-1] == "signature"

    def test_recv_window_injected_in_order(self) -> None:
        """recvWindow is inserted before timestamp when supplied."""
        params = Signer(SecretStr("s")).signed_params({"a": "1"}, timestamp=1, recv_window=5000)
        assert params["recvWindow"] == "5000"
        assert list(params) == ["a", "recvWindow", "timestamp", "signature"]

    def test_recv_window_not_overridden(self) -> None:
        """A caller-supplied recvWindow is kept."""
        params = Signer(SecretStr("s")).signed_params(
            {"recvWindow": "1000"}, timestamp=1, recv_window=5000
        )
        assert params["recvWindow"] == "1000"

    def test_reorder_changes_signature(self) -> None:
        """Reordering params changes the signature (order is load-bearing)."""
        signer = Signer(SecretStr("s"))
        a = signer.signed_params({"x": "1", "y": "2"}, timestamp=1)
        b = signer.signed_params({"y": "2", "x": "1"}, timestamp=1)
        assert a["signature"] != b["signature"]

    def test_empty_params(self) -> None:
        """With no params, only timestamp and signature are present."""
        params = Signer(SecretStr("s")).signed_params(None, timestamp=1)
        assert list(params) == ["timestamp", "signature"]
