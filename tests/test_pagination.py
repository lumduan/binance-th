"""Tests for time-window pagination (ADR-0016)."""

from collections.abc import AsyncIterator, Callable, Sequence


async def _collect(agen: AsyncIterator[int]) -> list[int]:
    return [x async for x in agen]


def _fetcher(pages: dict[int, list[int]]) -> tuple[Callable[[int, int], object], list[int]]:
    """A fetch(window_start, end) that serves scripted pages keyed by window_start."""
    calls: list[int] = []

    async def fetch(window_start: int, _end: int) -> Sequence[int]:
        calls.append(window_start)
        return list(pages.get(window_start, []))

    return fetch, calls


class TestIterTimeWindows:
    """The generic paginator."""

    async def test_single_short_page(self) -> None:
        """A page shorter than the limit ends iteration after one fetch."""
        from binance_th.pagination import iter_time_windows

        fetch, calls = _fetcher({0: [10, 20, 30]})
        out = await _collect(
            iter_time_windows(
                fetch, start_time=0, end_time=100, page_limit=5, window_key=lambda x: x
            )
        )
        assert out == [10, 20, 30]
        assert len(calls) == 1

    async def test_multi_window_dedups_boundary(self) -> None:
        """An inclusive-startTime boundary row is not double-yielded."""
        from binance_th.pagination import iter_time_windows

        fetch, _ = _fetcher({0: [10, 20, 30], 30: [30, 40, 50], 50: [50]})
        out = await _collect(
            iter_time_windows(
                fetch, start_time=0, end_time=100, page_limit=3, window_key=lambda x: x
            )
        )
        assert out == [10, 20, 30, 40, 50]
        assert out == sorted(set(out))

    async def test_half_open_end_excludes_boundary(self) -> None:
        """A row at or beyond end_time is excluded (half-open)."""
        from binance_th.pagination import iter_time_windows

        fetch, _ = _fetcher({0: [10, 20, 30]})
        out = await _collect(
            iter_time_windows(
                fetch, start_time=0, end_time=20, page_limit=5, window_key=lambda x: x
            )
        )
        assert out == [10]

    async def test_no_forward_progress_terminates(self) -> None:
        """A server that never advances the window still terminates."""
        from binance_th.pagination import iter_time_windows

        async def fetch(_ws: int, _end: int) -> Sequence[int]:
            return [5, 5, 5]

        out = await _collect(
            iter_time_windows(
                fetch, start_time=5, end_time=100, page_limit=3, window_key=lambda x: x
            )
        )
        assert out == [5, 5, 5]
