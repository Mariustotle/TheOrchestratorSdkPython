import asyncio

class DynamicSemaphore:
    def __init__(self, initial_limit: int):
        self._semaphore = asyncio.Semaphore(initial_limit)
        self._limit = initial_limit
        self._lock = asyncio.Lock()

        # for wait_for_release()
        self._checked_out = 0
        self._zero_event = asyncio.Event()
        self._zero_event.set()   # initially, nothing is checked out

    async def acquire(self):
        await self._semaphore.acquire()
        async with self._lock:
            self._checked_out += 1
            self._zero_event.clear()
    
    def _do_release(self):
        # this runs back on the loop thread
        self._checked_out -= 1
        if self._checked_out == 0:
            self._zero_event.set()

    def release(self):
        self._semaphore.release()
        asyncio.get_event_loop().call_soon_threadsafe(self._do_release)

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.release()

    async def set_new_limit(self, new_limit: int):
        async with self._lock:
            diff = new_limit - self._limit
            if diff > 0:
                for _ in range(diff):
                    self._semaphore.release()
            elif diff < 0:
                for _ in range(-diff):
                    await self._semaphore.acquire()
            self._limit = new_limit

    def current_limit(self):
        return self._limit

    async def wait_for_all_released(self):
        """
        Block until everything that’s been acquired has been released.
        """
        await self._zero_event.wait()
