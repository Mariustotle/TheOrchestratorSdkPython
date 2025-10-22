from collections import OrderedDict
from threading import RLock

from typing import List

from orchestrator_sdk.seedworks.logger import Logger

logger = Logger.get_instance()

class MessageDispatchedQueue:

    def __init__(self, capacity: int = 200) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self._capacity: int = capacity
        self._odict: OrderedDict[int, None] = OrderedDict() 
        self._lock: RLock = RLock()


    def try_add(self, id: int) -> bool:
        with self._lock:
            if id in self._odict:

                logger.warning(f'ID "{id}" already in recent queue – duplicate ignored.')
                return False

            self._odict[id] = None 

            if len(self._odict) > self._capacity:
                oldest, _ = self._odict.popitem(last=False)
                # logger.debug('Evicted oldest ID "%s" to maintain capacity.', oldest)

            return True

    def try_remove(self, id: int) -> bool:
        with self._lock:
            removed = self._odict.pop(id, None) is not None
            return removed

    def contains(self, id: int) -> bool:
        with self._lock:
            return id in self._odict

    def snapshot(self) -> List[int]:
        with self._lock:
            return list(self._odict.keys())

    def __len__(self) -> int:
        return len(self._odict)

    def __iter__(self):
        """Iterate oldest ➜ newest without external locking."""
        return iter(self.snapshot())
