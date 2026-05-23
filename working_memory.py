"""
working_memory.py
Week 1 deliverable — AI Memory Bus

What this file teaches you:
  Monday  → Python classes, dicts, O(1) get/set
  Tuesday → heapq (min-heap), TTL expiry in O(log n)
  Wednesday → OrderedDict, LRU eviction in O(1)

Every line is commented so you can explain it in an interview.
"""

import time
import heapq
from collections import OrderedDict


# ─────────────────────────────────────────────
# The WorkingMemory class
# Think of this as a mini-Redis running in RAM.
# ─────────────────────────────────────────────

class WorkingMemory:
    """
    A RAM-only key-value store where:
      - every entry has a TTL (time-to-live in seconds)
      - entries expire automatically via a min-heap
      - when the store is full, the least-recently-used entry is evicted
    """

    def __init__(self, max_size: int = 500):
        """
        max_size: maximum number of live keys allowed at once.
        Once full, the key touched least recently is dropped.
        """

        # ── Monday: the core store ──────────────────────────────────────
        # Why OrderedDict instead of plain dict?
        # OrderedDict tracks insertion/access ORDER — we need that for LRU.
        # A plain dict (Python 3.7+) preserves insertion order but
        # has no built-in move_to_end(), so LRU would cost O(n).
        # OrderedDict gives us move_to_end() in O(1).
        self._store: OrderedDict = OrderedDict()
        # Every value stored as (actual_value, expire_at_unix_timestamp)

        self._max_size = max_size

        # ── Tuesday: the TTL heap ───────────────────────────────────────
        # This is a min-heap of (expire_at, key) tuples.
        # Python's heapq always keeps the SMALLEST item at index [0].
        # So heap[0] is always the NEXT key to expire — O(1) to peek.
        # Popping is O(log n).
        self._ttl_heap: list = []

    # ────────────────────────────────────────────────────────────────────
    # SET  —  write a key with a TTL
    # ────────────────────────────────────────────────────────────────────
    def set(self, key: str, value, ttl: int) -> None:
        """
        Store key=value, expiring ttl seconds from now.

        Time complexity:
          dict write   → O(1)
          heap push    → O(log n)
          LRU evict    → O(1)
        """

        # Calculate the absolute expiry time once, so get() is simple
        expire_at = time.time() + ttl

        # Write to the store (or overwrite if key already exists)
        # We store a tuple: (value, expire_at)
        self._store[key] = (value, expire_at)

        # ── Wednesday: LRU — mark this key as "most recently used" ──────
        # move_to_end() pushes this key to the END of the OrderedDict.
        # The FRONT of the dict = least recently used = next to evict.
        self._store.move_to_end(key)

        # Evict oldest key if we've exceeded max_size
        self._evict_if_full()

        # ── Tuesday: push to the TTL heap ───────────────────────────────
        # We push (expire_at, key) — Python compares tuples left-to-right,
        # so the heap is sorted by expire_at. Soonest expiry = smallest.
        heapq.heappush(self._ttl_heap, (expire_at, key))

    # ────────────────────────────────────────────────────────────────────
    # GET  —  read a key (returns None if missing or expired)
    # ────────────────────────────────────────────────────────────────────
    def get(self, key: str):
        """
        Return the value for key, or None if:
          - key doesn't exist
          - key has expired

        Time complexity: O(1) dict lookup
        """

        # First check: is the key even in the store?
        if key not in self._store:
            return None

        value, expire_at = self._store[key]

        # Second check: has it expired?
        if time.time() > expire_at:
            # Lazy deletion — remove it now that we noticed it's dead
            del self._store[key]
            return None

        # ── Wednesday: LRU — mark this key as "most recently used" ──────
        # Because we just accessed it, it should be last to be evicted.
        self._store.move_to_end(key)

        return value

    # ────────────────────────────────────────────────────────────────────
    # DELETE  —  remove a key immediately
    # ────────────────────────────────────────────────────────────────────
    def delete(self, key: str) -> bool:
        """Remove a key. Returns True if it existed, False otherwise."""
        if key in self._store:
            del self._store[key]
            return True
        return False

    # ────────────────────────────────────────────────────────────────────
    # KEYS  —  list all currently live keys
    # ────────────────────────────────────────────────────────────────────
    def keys(self) -> list:
        """
        Return all keys that are still alive (not expired).
        Also evicts any expired entries it finds — keeps the store clean.
        """
        self._evict_expired()

        now = time.time()
        live = []
        for key, (value, expire_at) in self._store.items():
            if time.time() <= expire_at:
                live.append(key)
        return live

    # ────────────────────────────────────────────────────────────────────
    # FLUSH  —  wipe everything
    # ────────────────────────────────────────────────────────────────────
    def flush(self) -> None:
        """Clear all working memory. Used at session end."""
        self._store.clear()
        self._ttl_heap.clear()

    # ────────────────────────────────────────────────────────────────────
    # PRIVATE HELPERS
    # ────────────────────────────────────────────────────────────────────

    def _evict_expired(self) -> None:
        """
        ── Tuesday: min-heap TTL eviction ──

        Pop entries off the heap as long as the top entry has expired.
        heap[0] is always the SOONEST to expire (min-heap property).

        Why not just loop through self._store?
        Because that's O(n). Peeking heap[0] is O(1).
        Only when we confirm it's expired do we pop — O(log n).
        So for a store with 10,000 keys but only 3 expired,
        we do 3 pops, not 10,000 comparisons.
        """
        now = time.time()

        while self._ttl_heap:
            # Peek at the soonest-expiring entry — O(1)
            next_expire, next_key = self._ttl_heap[0]

            if next_expire > now:
                # The earliest expiry is still in the future.
                # Nothing else can have expired — stop checking.
                break

            # This entry has expired — pop it from the heap — O(log n)
            heapq.heappop(self._ttl_heap)

            # Only delete from the store if it hasn't been overwritten.
            # (A key can be set twice with different TTLs; the old heap
            #  entry becomes a stale ghost — we check expire_at matches.)
            if next_key in self._store:
                _, stored_expire = self._store[next_key]
                if stored_expire == next_expire:
                    del self._store[next_key]

    def _evict_if_full(self) -> None:
        """
        ── Wednesday: LRU eviction ──

        If the store has reached max_size, remove the least-recently-used
        key — that's the key at the FRONT of the OrderedDict.

        popitem(last=False) removes from the front in O(1).
        This works because every get() and set() calls move_to_end(),
        so the front is always the key nobody has touched longest.
        """
        while len(self._store) > self._max_size:
            # Remove the oldest (front) item
            oldest_key, _ = self._store.popitem(last=False)
            # We don't bother cleaning the heap — _evict_expired handles
            # ghost entries lazily the next time keys() or set() runs.


# ─────────────────────────────────────────────
# Manual tests — run this file to verify
# ─────────────────────────────────────────────

if __name__ == "__main__":

    print("=" * 50)
    print("WorkingMemory — manual tests")
    print("=" * 50)

    wm = WorkingMemory(max_size=3)

    # ── Test 1: basic set/get ─────────────────
    print("\n[Test 1] Basic set and get")
    wm.set("current_task", "Building cache server", ttl=10)
    result = wm.get("current_task")
    assert result == "Building cache server", f"Expected 'Building cache server', got {result}"
    print(f"  current_task = '{result}'  ✓")

    # ── Test 2: missing key ───────────────────
    print("\n[Test 2] Missing key returns None")
    result = wm.get("nonexistent_key")
    assert result is None, f"Expected None, got {result}"
    print(f"  nonexistent_key = {result}  ✓")

    # ── Test 3: TTL expiry ────────────────────
    print("\n[Test 3] TTL expiry (1-second key)")
    wm.set("short_lived", "gone soon", ttl=1)
    assert wm.get("short_lived") == "gone soon", "Should be alive"
    print("  alive before expiry  ✓")
    print("  sleeping 2 seconds...")
    time.sleep(2)
    result = wm.get("short_lived")
    assert result is None, f"Expected None after expiry, got {result}"
    print(f"  expired → {result}  ✓")

    # ── Test 4: LRU eviction ──────────────────
    print("\n[Test 4] LRU eviction (max_size=3)")
    wm2 = WorkingMemory(max_size=3)
    wm2.set("a", "apple",  ttl=300)
    wm2.set("b", "banana", ttl=300)
    wm2.set("c", "cherry", ttl=300)

    # Touch 'a' so it becomes most-recently-used
    _ = wm2.get("a")

    # Adding 'd' should evict 'b' (the least-recently-used now)
    wm2.set("d", "date", ttl=300)

    assert wm2.get("b") is None,     "b should have been evicted  ✓"
    assert wm2.get("a") == "apple",  "a should survive  ✓"
    assert wm2.get("c") == "cherry", "c should survive  ✓"
    assert wm2.get("d") == "date",   "d should survive  ✓"
    print("  'b' evicted (LRU), 'a', 'c', 'd' survive  ✓")

    # ── Test 5: delete ────────────────────────
    print("\n[Test 5] Manual delete")
    wm2.set("temp", "delete me", ttl=300)
    wm2.delete("temp")
    assert wm2.get("temp") is None
    print("  deleted key returns None  ✓")

    # ── Test 6: flush ─────────────────────────
    print("\n[Test 6] Flush clears everything")
    wm2.flush()
    assert wm2.keys() == []
    print("  all keys gone after flush  ✓")

    print("\n" + "=" * 50)
    print("All tests passed. WorkingMemory is ready.")
    print("=" * 50)
