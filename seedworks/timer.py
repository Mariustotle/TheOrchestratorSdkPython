import time
from datetime import datetime
from typing import Optional


class TimerStats:
    def __init__(self, name: str):
        self.name = name
        self.steps: dict[str, float] = {}
        self.start_time: datetime | None = None
        self.end_time: datetime | None = None

    def display_summary(self, additional_info:Optional[str] = None) -> str:
        if not (self.start_time and self.end_time):
            return f"No complete timing for [{self.name}]"
        total_duration = (self.end_time - self.start_time).total_seconds()

        if self.steps:
            slowest_step = max(self.steps, key=self.steps.get)
            slowest_pct = (self.steps[slowest_step] / total_duration) * 100
            step_details = ", ".join(f"'{k}' @ [{v:.3f}]s" for k, v in self.steps.items())
        else:
            slowest_step = "n/a"
            slowest_pct = 0.0
            step_details = "no steps recorded"

        add_info = '' if additional_info is None else f' Additional Info: {additional_info}'

        return (
            f"Performance stats for '{self.name}': [{total_duration:.3f}]s total, "
            f"slowest step '{slowest_step}' was [{self.steps[slowest_step]:.3f}]s at [{slowest_pct:.1f}]% of time. "
            f"Steps: {step_details}.{add_info}"
        )


class Timer:
    """
    Context manager that measures the duration of its block
    and records it into a shared TimerStats.
    
    Usage:
        stats = TimerStats("MyBatch")
        with Timer("MyBatch", stats):
            with Timer("Step A"):
                ...
            with Timer("Step B"):
                ...
        print(stats.display_summary())
    """
    # holds the current root TimerStats for nested timers
    _current_stats: TimerStats | None = None

    def __init__(self, name: str, stats: TimerStats | None = None):
        self.name = name
        # if an explicit stats object is passed, this is the root timer
        self._is_root = isinstance(stats, TimerStats)
        self.stats = stats if self._is_root else None
        self._t0: float | None = None

    def __enter__(self):
        # root timer: initialize or adopt passed-in stats
        if self._is_root:
            if self.stats.start_time is None:
                self.stats.start_time = datetime.now()
            Timer._current_stats = self.stats

        # nested timer: pick up the current root stats
        elif Timer._current_stats is not None:
            self.stats = Timer._current_stats

        # neither passed nor in a root: make a new root
        else:
            self.stats = TimerStats(self.name)
            self.stats.start_time = datetime.now()
            Timer._current_stats = self.stats
            self._is_root = True  # this one now behaves as root

        # start high-precision counter
        self._t0 = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        elapsed = time.perf_counter() - (self._t0 or 0)     

        # if this is the root timer, close it out
        if self._is_root and self.stats.end_time is None:
            self.stats.end_time = datetime.now()
            Timer._current_stats = None

        # record this step
        if not self._is_root:
            self.stats.steps[self.name] = elapsed

        # do not suppress exceptions
        return False
