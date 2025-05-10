from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional
import random

class ServiceUnavailableError(TimeoutError):
    """Raised when the simulator is deliberately put offline."""
    pass

class AvailabilitySimulator:
    """Cycle between ‘online’ and ‘offline’ in one shared singleton."""

    failed_count = 0
    offline_after: int = 60
    max_offline_minutes: int = random.randint(2, 5)
    offline_duration:int[Optional] = None

    _instance: Optional["AvailabilitySimulator"] = None
    _last_cycle_start: datetime
    _available_after: Optional[datetime]

    def __new__(cls) -> "AvailabilitySimulator":
        raise RuntimeError("Use AvailabilitySimulator.instance()")

    @classmethod
    def instance(cls) -> "AvailabilitySimulator":
        if cls._instance is None:
            obj = super().__new__(cls)
            obj._last_cycle_start = datetime.utcnow()
            obj._available_after = None
            cls._instance = obj
        return cls._instance

    # ───────── behaviour ─────────
    def is_available(self) -> bool:
        now = datetime.utcnow()

        if self._available_after and now < self._available_after:
            failed_count += 1
            return False                    # still offline

        if self._available_after:           # outage ended
            self._available_after = None
            self._last_cycle_start = now
            self.failed_count = 0
            return True

        if now - self._last_cycle_start > timedelta(minutes=self.offline_after):
            self.offline_duration = random.randint(1, self.max_offline_minutes)
            self._available_after = now + timedelta(minutes=self.offline_duration)
            failed_count += 1
            return False                    # just went offline

        return True                         # still online

    def simulate_unavailable(self) -> None:
        remaining_time = datetime.utcnow() - self._available_after

        raise ServiceUnavailableError(
            f"Simulated client offline, remaining outage time [{remaining_time.seconds}s] - Blocked Requests: [{self.failed_count}], Duration: [{self.offline_duration}min], Outage End: [{self._available_after.isoformat(timespec='seconds')}]."
        )
