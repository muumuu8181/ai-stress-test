import time
import os
import pytest
import threading
from components.lru_cache_007.lru_cache import LRUCache

def test_basic_put_get():
    cache = LRUCache(capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == 1
    assert cache.get("b") == 2
    assert cache.get("c") is None

def test_lru_eviction():
    cache = LRUCache(capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("a") # "a" is now MRU
    cache.put("c", 3) # "b" should be evicted
    assert cache.get("a") == 1
    assert cache.get("c") == 3
    assert cache.get("b") is None
    assert cache.eviction_count == 1

def test_ttl_expiration():
    cache = LRUCache(capacity=10, default_ttl=0.1)
    cache.put("a", 1)
    assert cache.get("a") == 1
    time.sleep(0.15)
    assert cache.get("a") is None
    assert cache.miss_count == 1

def test_per_item_ttl():
    cache = LRUCache(capacity=10, default_ttl=1.0)
    cache.put("a", 1, ttl=0.1)
    cache.put("b", 2) # default ttl 1.0
    time.sleep(0.15)
    assert cache.get("a") is None
    assert cache.get("b") == 2

def test_statistics():
    cache = LRUCache(capacity=2)
    cache.put("a", 1)
    cache.get("a") # hit
    cache.get("b") # miss
    assert cache.hit_count == 1
    assert cache.miss_count == 1
    assert cache.hit_rate == 0.5

def test_edge_cases():
    with pytest.raises(ValueError):
        LRUCache(capacity=0)

    cache = LRUCache(capacity=1)
    cache.put(None, "null_key")
    assert cache.get(None) == "null_key"

    cache.put("key", None)
    assert cache.get("key") is None # But it is a hit if we look at stats?
    # Wait, if get returns None, we can't distinguish between "miss" and "stored None".
    # However, my implementation returns None for miss AND it increments miss_count.
    # Let's check stats.

    cache = LRUCache(capacity=1)
    cache.put("a", None)
    res = cache.get("a")
    assert res is None
    assert cache.hit_count == 1
    assert cache.miss_count == 0

def test_concurrency():
    cache = LRUCache(capacity=100)
    def worker(id):
        for i in range(100):
            cache.put(f"key-{id}-{i}", i)
            cache.get(f"key-{id}-{i}")

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Check if total hits + misses = total get calls (10 * 100 = 1000)
    assert cache.hit_count + cache.miss_count == 1000

def test_memory_leak():
    # Simulate heavy usage and check if capacity is respected
    cache = LRUCache(capacity=10)
    for i in range(1000):
        cache.put(i, i)
    assert len(cache.cache) <= 10
    assert cache.eviction_count == 990

def test_persistence(tmp_path):
    filepath = str(tmp_path / "cache.pkl")
    cache = LRUCache(capacity=5)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("a")

    cache.persist(filepath)

    new_cache = LRUCache(capacity=1) # Capacity will be overwritten by restore
    new_cache.restore(filepath)

    assert new_cache.capacity == 5
    assert new_cache.hit_count == 1 # Stats are also restored
    assert new_cache.get("a") == 1
    assert new_cache.get("b") == 2

def test_callbacks():
    evicted = []
    expired = []
    def on_evict(k, v): evicted.append((k, v))
    def on_expire(k, v): expired.append((k, v))

    cache = LRUCache(capacity=2, on_evict=on_evict, on_expire=on_expire)

    # Test eviction
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3) # "a" should be evicted
    assert evicted == [("a", 1)]

    # Test expiration via get
    cache.put("d", 4, ttl=0.01)
    time.sleep(0.02)
    cache.get("d")
    assert expired == [("d", 4)]

    # Test expiration via put (eviction of expired item)
    expired.clear()
    cache.put("e", 5, ttl=0.01)
    time.sleep(0.02)
    cache.put("f", 6) # "b" or "c" would be evicted if not for "e" being expired and at the front?
    # Wait, LRU is "b", "c", "e". "b" is front.
    # If "b" is not expired, it gets evicted.
    # Let's make "b" expire.

    cache = LRUCache(capacity=2, on_evict=on_evict, on_expire=on_expire)
    evicted.clear()
    expired.clear()
    cache.put("a", 1, ttl=0.01)
    cache.put("b", 2)
    time.sleep(0.02)
    cache.put("c", 3) # "a" is at front and is expired.
    assert expired == [("a", 1)]
    assert evicted == []
