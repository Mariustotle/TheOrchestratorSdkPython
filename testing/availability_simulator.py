from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional

class ServiceUnavailableError(TimeoutError):
    """Raised when the simulator is deliberately put offline."""
    pass

class AvailabilitySimulator:
    """Cycle between ‘online’ and ‘offline’ in one shared singleton."""

    minutes_until_offline: int = 5
    offline_in_minutes: int = 1

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

        if now - self._last_cycle_start > timedelta(minutes=self.minutes_until_offline):
            self._available_after = now + timedelta(minutes=self.offline_in_minutes)
            return False                    # just went offline

        return True                         # still online

    def simulate_unavailable(self) -> None:
        raise ServiceUnavailableError(
            f"Service forced offline until {self._available_after.isoformat(timespec='seconds')} UTC"
        )
