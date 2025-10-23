from collections import OrderedDict
from threading import RLock
from datetime import datetime

from typing import List

from orchestrator_sdk.seedworks.logger import Logger

logger = Logger.get_instance()

class MessageDispatchedQueue:

    def __init__(self, capacity: int = 200) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self._capacity: int = capacity
        self._odict: OrderedDict[int, datetime] = OrderedDict() 
        self._lock: RLock = RLock()


    def try_add(self, id: int) -> bool:
        with self._lock:
            if id in self._odict:

                logger.info(f'ID "{id}" already in-progress. Ignoring the request.')
                return False

            self._odict[id] = datetime.utcnow() 

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
        
    def get(self, id: int) -> datetime:
        with self._lock:
            return self._odict.get(id)

    def snapshot(self) -> List[int]:
        with self._lock:
            return list(self._odict.keys())

    def __len__(self) -> int:
        return len(self._odict)

    def __iter__(self):
        """Iterate oldest ➜ newest without external locking."""
        return iter(self.snapshot())
