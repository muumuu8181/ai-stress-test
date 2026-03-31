import threading
import time
import pickle
from collections import OrderedDict
from typing import Any, Optional, Callable, Tuple

class LRUCache:
    """
    A thread-safe LRU (Least Recently Used) cache with TTL (Time To Live) support.

    This cache supports:
    - Fixed capacity with LRU eviction.
    - Default TTL and per-item custom TTL.
    - Thread-safety using a reentrant lock.
    - Statistics tracking (hit rate, miss count, eviction count).
    - Event callbacks for eviction and expiration.
    - Persistence to and restoration from disk.
    """
    def __init__(
        self,
        capacity: int,
        default_ttl: Optional[float] = None,
        on_evict: Optional[Callable[[Any, Any], None]] = None,
        on_expire: Optional[Callable[[Any, Any], None]] = None,
    ) -> None:
        """
        Initialize the LRUCache.

        Args:
            capacity: Maximum number of items the cache can hold.
            default_ttl: Default time-to-live in seconds for items. If None, items never expire by default.
            on_evict: Optional callback function called when an item is evicted due to capacity.
                     Receives (key, value) as arguments.
            on_expire: Optional callback function called when an item expires.
                      Receives (key, value) as arguments.

        Raises:
            ValueError: If capacity is not positive.
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")

        self.capacity = capacity
        self.default_ttl = default_ttl
        self.on_evict = on_evict
        self.on_expire = on_expire

        # cache stores (value, expiry_time)
        # expiry_time is absolute time (float). float('inf') if no TTL.
        self.cache: OrderedDict[Any, Tuple[Any, float]] = OrderedDict()
        self.lock = threading.RLock() # Use RLock just in case internal methods call each other

        self.hit_count = 0
        self.miss_count = 0
        self.eviction_count = 0

    @property
    def hit_rate(self) -> float:
        """
        Calculate the cache hit rate.

        Returns:
            The ratio of hits to total requests (hits + misses). Returns 0.0 if no requests were made.
        """
        with self.lock:
            total = self.hit_count + self.miss_count
            if total == 0:
                return 0.0
            return self.hit_count / total

    def get(self, key: Any) -> Any:
        """
        Retrieve an item from the cache.

        Args:
            key: The key to look up.

        Returns:
            The cached value if present and not expired, otherwise None.
        """
        with self.lock:
            if key not in self.cache:
                self.miss_count += 1
                return None

            value, expiry = self.cache[key]
            if expiry < time.time():
                # Expired
                self.cache.pop(key)
                self.miss_count += 1
                if self.on_expire:
                    self.on_expire(key, value)
                return None

            # Update LRU by moving the accessed key to the end
            self.cache.move_to_end(key)
            self.hit_count += 1
            return value

    def put(self, key: Any, value: Any, ttl: Optional[float] = None) -> None:
        """
        Add or update an item in the cache.

        Args:
            key: The key to store.
            value: The value to store.
            ttl: Custom time-to-live in seconds for this item.
                 If None, the default_ttl specified during initialization is used.
        """
        with self.lock:
            # If the key is already present, just update it
            if key in self.cache:
                current_ttl = ttl if ttl is not None else self.default_ttl
                expiry = time.time() + current_ttl if current_ttl is not None else float('inf')
                self.cache[key] = (value, expiry)
                self.cache.move_to_end(key)
                return

            # Key is new. Check if we need to make space.
            if len(self.cache) >= self.capacity:
                # First, try to remove all expired items
                self._cleanup_expired()

                # If still at capacity, perform LRU eviction
                if len(self.cache) >= self.capacity:
                    self._evict_lru()

            # Calculate expiry time
            current_ttl = ttl if ttl is not None else self.default_ttl
            expiry = time.time() + current_ttl if current_ttl is not None else float('inf')

            # Add or update item and move to end (most recently used)
            self.cache[key] = (value, expiry)
            self.cache.move_to_end(key)

    def _cleanup_expired(self) -> None:
        """
        Internal method to remove all expired items from the cache.
        """
        now = time.time()
        expired_keys = [k for k, (v, exp) in self.cache.items() if exp < now]
        for k in expired_keys:
            val, exp = self.cache.pop(k)
            # Note: Removal of expired items during cleanup is not counted as 'eviction'
            # but we trigger the callback.
            if self.on_expire:
                self.on_expire(k, val)

    def _evict_lru(self) -> None:
        """
        Internal method to evict the least recently used item.
        """
        if self.cache:
            key, (value, expiry) = self.cache.popitem(last=False)
            self.eviction_count += 1
            if expiry < time.time():
                if self.on_expire:
                    self.on_expire(key, value)
            else:
                if self.on_evict:
                    self.on_evict(key, value)

    def persist(self, filepath: str) -> None:
        """
        Save the current state of the cache to a file using pickle.

        .. warning::
           The pickle module is not secure. Only unpickle data you trust.
           It is possible to craft malicious pickle data which will execute
           arbitrary code during unpickling.

        Args:
            filepath: Path to the file where the cache state will be saved.
        """
        with self.lock:
            state = {
                'capacity': self.capacity,
                'default_ttl': self.default_ttl,
                'cache': self.cache,
                'hit_count': self.hit_count,
                'miss_count': self.miss_count,
                'eviction_count': self.eviction_count
            }
            with open(filepath, 'wb') as f:
                pickle.dump(state, f)

    def restore(self, filepath: str) -> None:
        """
        Restore the cache state from a file.

        .. warning::
           The pickle module is not secure. Only unpickle data you trust.
           It is possible to craft malicious pickle data which will execute
           arbitrary code during unpickling.

        Args:
            filepath: Path to the file containing the saved cache state.
        """
        with self.lock:
            with open(filepath, 'rb') as f:
                state = pickle.load(f)

            self.capacity = state.get('capacity', self.capacity)
            self.default_ttl = state.get('default_ttl', self.default_ttl)
            self.cache = state.get('cache', OrderedDict())
            self.hit_count = state.get('hit_count', 0)
            self.miss_count = state.get('miss_count', 0)
            self.eviction_count = state.get('eviction_count', 0)
