import asyncio
from collections import deque
from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from math import ceil
from typing import Deque, Optional


@dataclass(frozen=True)
class ReleaseEntry:
    utc_timestamp: datetime
    count: int


class ThroughputLimiter:
    """
    Async throughput limiter with:
    - sliding 1-minute release window
    - periodic refill ticks
    - bounded in-memory token buffer
    - async wait / try-wait support

    Example:
        limiter = ThroughputLimiter(rate_per_minute=600)

        await limiter.wait()

        acquired = await limiter.try_wait_async(timeout=10)
        if not acquired:
            # handle fallback
            pass

        await limiter.aclose()
    """

    def __init__(
        self,
        rate_per_minute: int,
        tick_interval: float = 2.0,
        start_immediately: bool = True,
    ) -> None:
        if rate_per_minute <= 0:
            raise ValueError("rate_per_minute must be greater than zero.")
        if tick_interval <= 0:
            raise ValueError("tick_interval must be greater than zero.")

        self._rate_per_minute = rate_per_minute
        self._tick_interval = tick_interval
        self._window_length = timedelta(minutes=1)

        ticks_per_minute = 60.0 / tick_interval
        self._refill_amount_per_tick = max(1, ceil(rate_per_minute / ticks_per_minute))

        # Roughly 10 seconds worth of tokens buffered
        self._buffer_capacity = max(1, ceil(rate_per_minute / 6.0))

        self._available_permits: asyncio.Queue[None] = asyncio.Queue(
            maxsize=self._buffer_capacity
        )
        self._release_history: Deque[ReleaseEntry] = deque()
        self._rolling_released_count = 0

        self._sync_lock = asyncio.Lock()
        self._closed = False
        self._refill_running = False
        self._refill_task: Optional[asyncio.Task[None]] = None

        if start_immediately:
            self._ensure_refill_running()

    @property
    def rate_per_minute(self) -> int:
        return self._rate_per_minute

    @property
    def refill_amount_per_tick(self) -> int:
        return self._refill_amount_per_tick

    @property
    def buffer_capacity(self) -> int:
        return self._buffer_capacity

    @property
    def current_buffered_count(self) -> int:
        return self._available_permits.qsize()

    @property
    def is_refill_running(self) -> bool:
        return self._refill_running

    async def current_rolling_usage(self) -> int:
        async with self._sync_lock:
            self._prune_expired_release_history_no_lock(self._utcnow())
            return self._rolling_released_count

    async def remaining_capacity_in_window(self) -> int:
        rolling = await self.current_rolling_usage()
        return max(0, self._rate_per_minute - rolling)

    def start(self) -> None:
        self._throw_if_closed()
        self._ensure_refill_running()

    async def wait(self) -> None:
        self._throw_if_closed()
        self._ensure_refill_running()

        await self._available_permits.get()

        # If the loop had paused because the buffer was full, consuming wakes it again.
        self._ensure_refill_running()

    async def try_wait_async(self, timeout: float) -> bool:
        self._throw_if_closed()
        self._ensure_refill_running()

        try:
            await asyncio.wait_for(self._available_permits.get(), timeout=timeout)
            self._ensure_refill_running()
            return True
        except asyncio.TimeoutError:
            return False

    def try_wait_nowait(self) -> bool:
        self._throw_if_closed()
        self._ensure_refill_running()

        try:
            self._available_permits.get_nowait()
            self._ensure_refill_running()
            return True
        except asyncio.QueueEmpty:
            return False

    def _ensure_refill_running(self) -> None:
        if self._closed or self._refill_running:
            return

        self._refill_running = True
        self._refill_task = asyncio.create_task(self._refill_loop())

    async def _refill_loop(self) -> None:
        try:
            while not self._closed:
                permits_to_release = 0
                should_pause_for_full_buffer = False

                async with self._sync_lock:
                    now = self._utcnow()
                    self._prune_expired_release_history_no_lock(now)

                    buffer_count = self._available_permits.qsize()
                    if buffer_count >= self._buffer_capacity:
                        should_pause_for_full_buffer = True
                    else:
                        remaining_buffer_space = self._buffer_capacity - buffer_count
                        remaining_sliding_capacity = (
                            self._rate_per_minute - self._rolling_released_count
                        )

                        # Do not stop when the sliding window is full.
                        # Just wait until older releases age out.
                        if remaining_sliding_capacity > 0:
                            permits_to_release = min(
                                self._refill_amount_per_tick,
                                remaining_buffer_space,
                                remaining_sliding_capacity,
                            )

                            if permits_to_release > 0:
                                self._release_history.append(
                                    ReleaseEntry(now, permits_to_release)
                                )
                                self._rolling_released_count += permits_to_release

                for _ in range(permits_to_release):
                    try:
                        self._available_permits.put_nowait(None)
                    except asyncio.QueueFull:
                        break

                if should_pause_for_full_buffer:
                    self._refill_running = False
                    return

                await asyncio.sleep(self._tick_interval)

        except asyncio.CancelledError:
            pass
        finally:
            self._refill_running = False

    def _prune_expired_release_history_no_lock(self, utc_now: datetime) -> None:
        while self._release_history:
            oldest = self._release_history[0]
            if (utc_now - oldest.utc_timestamp) < self._window_length:
                break

            removed = self._release_history.popleft()
            self._rolling_released_count -= removed.count

        if self._rolling_released_count < 0:
            self._rolling_released_count = 0

    def _throw_if_closed(self) -> None:
        if self._closed:
            raise RuntimeError("ThroughputLimiter has been closed.")

    async def aclose(self) -> None:
        if self._closed:
            return

        self._closed = True

        if self._refill_task is not None:
            self._refill_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._refill_task

    async def __aenter__(self) -> "ThroughputLimiter":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    @staticmethod
    def _utcnow() -> datetime:
        return datetime.now(timezone.utc)