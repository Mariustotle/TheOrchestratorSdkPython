from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional
import random

class ServiceUnavailableError(TimeoutError):
    """Raised when the simulator is deliberately put offline."""
    pass

class AvailabilitySimulator:
    """Cycle between ‘online’ and ‘offline’ in one shared singleton."""

    offline_after: int = 30
    max_offline_minutes: int = 5
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
            return False                    # still offline

        if self._available_after:           # outage ended
            self._available_after = None
            self._last_cycle_start = now
            return True

        if now - self._last_cycle_start > timedelta(minutes=self.offline_after):
            self.offline_duration = random.randint(1, self.max_offline_minutes)
            self._available_after = now + timedelta(minutes=self.offline_duration)
            return False                    # just went offline

        return True                         # still online

    def simulate_unavailable(self) -> None:
        raise ServiceUnavailableError(
            f"Simulated client offline for [{self.offline_duration}] minutes until [{self._available_after.isoformat(timespec='seconds')} UTC]"
        )
