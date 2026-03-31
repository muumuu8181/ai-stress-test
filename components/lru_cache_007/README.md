# LRU Cache with TTL

A thread-safe Least Recently Used (LRU) cache implementation in Python with support for Time-To-Live (TTL).

## Features

- **Capacity Management**: Automatically evicts the least recently used item when capacity is reached.
- **TTL Support**: Supports both global default TTL and per-item custom TTL.
- **Thread-Safe**: Uses a reentrant lock to ensure safety in multi-threaded environments.
- **Statistics Tracking**: Monitor cache performance with `hit_rate`, `miss_count`, and `eviction_count`.
- **Event Callbacks**: Register `on_evict` and `on_expire` hooks to handle item removal.
- **Persistence**: Save and restore the cache state to/from disk (via `pickle`).

## Installation

This component requires no external dependencies beyond the Python standard library and `pytest` for testing.

## Usage Example

```python
from components.lru_cache_007.lru_cache import LRUCache
import time

# Initialize cache with capacity 2 and 1-second default TTL
cache = LRUCache(capacity=2, default_ttl=1.0)

# Basic put and get
cache.put("key1", "value1")
print(cache.get("key1"))  # Output: value1

# Per-item custom TTL (0.1 seconds)
cache.put("key2", "value2", ttl=0.1)
time.sleep(0.2)
print(cache.get("key2"))  # Output: None (expired)

# LRU Eviction
cache.put("key3", "value3")
cache.put("key4", "value4") # key1 will be evicted (LRU)
print(cache.get("key1"))  # Output: None

# Statistics
print(f"Hit rate: {cache.hit_rate}")
print(f"Evictions: {cache.eviction_count}")

# Persistence
cache.persist("cache_state.pkl")
new_cache = LRUCache(capacity=2)
new_cache.restore("cache_state.pkl")
print(new_cache.get("key3")) # Output: value3
```

## API Reference

### `LRUCache(capacity, default_ttl=None, on_evict=None, on_expire=None)`
- `capacity`: Max items (int).
- `default_ttl`: Default expiry in seconds (float).
- `on_evict`: Callback `(key, value)`.
- `on_expire`: Callback `(key, value)`.

### Methods
- `get(key)`: Retrieve item. Returns `None` if miss or expired.
- `put(key, value, ttl=None)`: Insert/update item with optional custom TTL.
- `persist(filepath)`: Save state to file.
- `restore(filepath)`: Load state from file.

### Properties
- `hit_rate`: Ratio of hits to total requests.
- `hit_count`, `miss_count`, `eviction_count`: Raw counters.
