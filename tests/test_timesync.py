"""Tests for the server-time offset manager (ADR-0004)."""

from binance_th.timesync import TimeSync, default_now_ms


class TestTimeSync:
    """Tests for TimeSync."""

    def test_initial_state(self) -> None:
        """Before syncing, offset is zero and now_ms is the raw clock."""
        ts = TimeSync(clock=lambda: 1000)
        assert ts.offset_ms == 0
        assert ts.synced is False
        assert ts.now_ms() == 1000

    def test_update_computes_offset(self) -> None:
        """update sets the offset and flips synced."""
        ts = TimeSync(clock=lambda: 1000)
        assert ts.update(1500) == 500
        assert ts.synced is True
        assert ts.now_ms() == 1500

    def test_negative_offset(self) -> None:
        """A fast local clock yields a negative offset."""
        ts = TimeSync(clock=lambda: 2000)
        ts.update(1500)
        assert ts.offset_ms == -500

    def test_skew_lands_in_window(self) -> None:
        """A 30s-fast local clock is corrected back onto server time."""
        ts = TimeSync(clock=lambda: 1_000_000 + 30_000)
        ts.update(1_000_000)
        assert ts.now_ms() == 1_000_000

    def test_default_now_ms_is_positive(self) -> None:
        """The default clock returns a plausible epoch-ms value."""
        assert default_now_ms() > 1_600_000_000_000
