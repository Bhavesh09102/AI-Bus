import heapq
import time
from collections import OrderedDict


class WorkingMemory:
    def __init__(self, max_size: int = 500):
        self.max_size = max_size
        self._store: OrderedDict = OrderedDict()
        self._heap: list = []

    def set(self, key: str, value, ttl: float = 3600):
        expire_at = time.time() + ttl
        self._store[key] = (value, expire_at)
        self._store.move_to_end(key)
        heapq.heappush(self._heap, (expire_at, key))
        self._evict_if_full()

    def get(self, key: str):
        if key not in self._store:
            return None
        value, expire_at = self._store[key]
        if expire_at <= time.time():
            del self._store[key]
            return None
        self._store.move_to_end(key)
        return value

    def all_keys(self) -> dict:
        self._evict_expired()
        return {k: v for k, (v, _) in self._store.items()}

    def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False

    def flush(self):
        self._store.clear()
        self._heap.clear()

    def _evict_expired(self):
        now = time.time()
        while self._heap and self._heap[0][0] <= now:
            expire_at, key = heapq.heappop(self._heap)
            if key in self._store:
                _, stored_expire = self._store[key]
                if stored_expire == expire_at:
                    del self._store[key]

    def _evict_if_full(self):
        while len(self._store) > self.max_size:
            self._store.popitem(last=False)
