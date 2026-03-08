from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import RLock


@dataclass(frozen=True)
class _InFlightEntry:
    id: int
    added_at: datetime
    expires_at: datetime


class InFlightSet:

    def __init__(self, capacity: int = 10000, ttl: timedelta = timedelta(minutes=5)) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        if ttl <= timedelta(0):
            raise ValueError("ttl must be > 0")

        self._capacity = capacity
        self._ttl = ttl
        self._items: OrderedDict[int, _InFlightEntry] = OrderedDict()
        self._lock = RLock()
        self._disposed = False

    # ----------------------------
    # Public API
    # ----------------------------

    def try_add(self, id: int) -> bool:
        now = datetime.utcnow()

        with self._lock:
            self._ensure_not_disposed()

            self._cleanup_expired_no_throw(now)

            entry = self._items.get(id)
            if entry is not None and entry.expires_at > now:
                return False

            self._items.pop(id, None)

            self._items[id] = _InFlightEntry(
                id=id,
                added_at=now,
                expires_at=now + self._ttl
            )

            self._enforce_capacity_no_throw(now)
            return True

    def contains(self, id: int) -> bool:
        now = datetime.utcnow()

        with self._lock:
            self._ensure_not_disposed()

            entry = self._items.get(id)
            if entry is None:
                return False

            if entry.expires_at > now:
                return True

            self._items.pop(id, None)
            self._cleanup_expired_no_throw(now)
            return False

    def try_remove(self, id: int) -> bool:
        with self._lock:
            self._ensure_not_disposed()
            return self._items.pop(id, None) is not None

    @property
    def count(self) -> int:
        with self._lock:
            return len(self._items)

    # ----------------------------
    # Cleanup / Dispose
    # ----------------------------

    def clear(self) -> None:
        """
        Clears all in-flight items.
        """
        with self._lock:
            self._items.clear()

    def dispose(self) -> None:
        """
        Disposes the set and releases memory.
        After disposal the instance should not be used again.
        """
        with self._lock:
            if self._disposed:
                return

            self._items.clear()
            self._disposed = True

    # ----------------------------
    # Internal helpers
    # ----------------------------

    def _ensure_not_disposed(self) -> None:
        if self._disposed:
            raise RuntimeError("InFlightSet has been disposed")

    def _enforce_capacity_no_throw(self, now: datetime) -> None:
        self._cleanup_expired_no_throw(now)

        while len(self._items) > self._capacity:
            self._items.popitem(last=False)

    def _cleanup_expired_no_throw(self, now: datetime) -> None:
        while self._items:
            oldest_id, oldest_entry = next(iter(self._items.items()))
            if oldest_entry.expires_at > now:
                break
            self._items.pop(oldest_id, None)