import asyncio

class DynamicSemaphore:
    def __init__(self, initial_limit: int):
        self._semaphore = asyncio.Semaphore(initial_limit)
        self._limit = initial_limit
        self._lock = asyncio.Lock()

    async def acquire(self):
        await self._semaphore.acquire()

    def release(self):
        self._semaphore.release()

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
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
