from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import RLock


@dataclass(frozen=True)
class _Entry:
    id: int
    expires_at: datetime


class RecentSuccessTtlSet:
    """
    Tracks recently successful IDs with:
    - TTL expiry
    - bounded capacity
    - refresh-on-add behavior
    - oldest -> newest ordering by last add/refresh
    - thread safety
    """

    def __init__(self, capacity: int, ttl: timedelta) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        if ttl <= timedelta(0):
            raise ValueError("ttl must be > 0")

        self._capacity = capacity
        self._ttl = ttl
        self._items: OrderedDict[int, _Entry] = OrderedDict()
        self._lock = RLock()

    def try_add(self, id: int) -> bool:
        """
        Add/refresh a key as recently succeeded.
        Returns True if newly added, False if it already existed and was refreshed.
        """
        now = datetime.utcnow()
        expires_at = now + self._ttl

        with self._lock:
            self._cleanup_expired_no_throw(now)

            already_exists = id in self._items
            if already_exists:
                self._items.pop(id, None)

            self._items[id] = _Entry(id=id, expires_at=expires_at)
            self._enforce_capacity_no_throw(now)

            return not already_exists

    def contains(self, id: int) -> bool:
        """
        True if key exists and is not expired.
        Opportunistically removes expired keys.
        """
        now = datetime.utcnow()

        with self._lock:
            entry = self._items.get(id)
            if entry is None:
                return False

            if entry.expires_at > now:
                return True

            self._items.pop(id, None)
            self._cleanup_expired_no_throw(now)
            return False

    def try_remove(self, id: int) -> bool:
        """
        Removes a key if present.
        """
        with self._lock:
            return self._items.pop(id, None) is not None

    @property
    def count(self) -> int:
        with self._lock:
            return len(self._items)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()

    def dispose(self) -> None:
        """
        Included only for API similarity with the C# version.
        Not strictly needed in Python.
        """
        self.clear()

    # ---- internals ----

    def _enforce_capacity_no_throw(self, now: datetime) -> None:
        self._cleanup_expired_no_throw(now)

        while len(self._items) > self._capacity:
            self._items.popitem(last=False)  # remove oldest

    def _cleanup_expired_no_throw(self, now: datetime) -> None:
        while self._items:
            oldest_id, oldest_entry = next(iter(self._items.items()))
            if oldest_entry.expires_at > now:
                break
            self._items.pop(oldest_id, None)