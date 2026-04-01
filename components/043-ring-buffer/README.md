# Ring Buffer & Deque

A pure Python implementation of a fixed-size Ring Buffer and Double-Ended Queue (Deque) with support for various overflow strategies, thread-safety, and blocking operations.

## Features

- **Fixed-size Ring Buffer**: Efficiently manages a fixed amount of memory.
- **Double-ended Queue (Deque)**: Supports operations at both ends (`append`, `appendleft`, `pop`, `popleft`).
- **Overflow Strategies**:
  - `OVERWRITE`: Overwrites the oldest element (default).
  - `ERROR`: Raises a `Full` exception.
  - `DISCARD`: Quietly discards the new element.
- **Thread-safe**: `ThreadSafeRingDeque` provides atomic operations using locks.
- **Blocking Operations**: `BlockingRingDeque` supports blocking `put` and `get` with optional timeouts.
- **Iterator Support**: Standard Python iteration from left to right.
- **Type Hints**: Fully typed API for better developer experience.

## Usage

### Basic RingDeque

```python
from ring_buffer.deque import RingDeque, OverflowStrategy

# Create a deque with max size 3 and overwrite strategy
dq = RingDeque(maxlen=3, strategy=OverflowStrategy.OVERWRITE)

dq.append(1)
dq.append(2)
dq.append(3)
dq.append(4)  # Overwrites 1

print(list(dq))  # Output: [2, 3, 4]
print(dq.popleft())  # Output: 2
```

### Thread-Safe Deque

```python
from ring_buffer.deque import ThreadSafeRingDeque

dq = ThreadSafeRingDeque(maxlen=10)
# Safe to use in multi-threaded environments
dq.append("safe")
```

### Blocking Deque (Producer-Consumer)

```python
import threading
from ring_buffer.deque import BlockingRingDeque

dq = BlockingRingDeque(maxlen=5)

def producer():
    for i in range(10):
        dq.put(i)  # Blocks if full

def consumer():
    for i in range(10):
        item = dq.get()  # Blocks if empty
        print(f"Consumed {item}")

threading.Thread(target=producer).start()
threading.Thread(target=consumer).start()
```

## API Reference

### `RingDeque[T](maxlen: int, strategy: OverflowStrategy)`

- `append(item: T)`: Add to right.
- `appendleft(item: T)`: Add to left.
- `pop() -> T`: Remove from right.
- `popleft() -> T`: Remove from left.
- `peek() -> T`: View rightmost.
- `peekleft() -> T`: View leftmost.
- `maxlen`: Property returning max capacity.
- `from_iterable(iterable, maxlen, strategy)`: Class method to create from iterable.

### `BlockingRingDeque[T]` (Inherits from ThreadSafeRingDeque)

- `put(item: T, block: bool = True, timeout: float = None)`: Add item to right.
- `get(block: bool = True, timeout: float = None) -> T`: Remove item from left.

## License

MIT
