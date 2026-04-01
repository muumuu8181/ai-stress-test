from enum import Enum
from typing import Any, Iterable, Iterator, List, Optional, TypeVar, Type, Generic
import threading
import time

T = TypeVar("T")

class DequeError(Exception):
    """Base class for deque exceptions."""
    pass

class Full(DequeError):
    """Exception raised when the deque is full."""
    pass

class Empty(DequeError):
    """Exception raised when the deque is empty."""
    pass

class OverflowStrategy(Enum):
    """Strategies for handling overflow in a fixed-size ring buffer."""
    OVERWRITE = "overwrite"
    ERROR = "error"
    DISCARD = "discard"

class RingDeque(Generic[T]):
    """
    A fixed-size double-ended queue (deque) implemented using a ring buffer.

    Args:
        maxlen: The maximum number of elements the deque can hold.
        strategy: The strategy to use when the deque is full and a new element is added via append/appendleft.
    """
    def __init__(self, maxlen: int, strategy: OverflowStrategy = OverflowStrategy.OVERWRITE) -> None:
        if maxlen <= 0:
            raise ValueError("maxlen must be greater than 0")
        self._maxlen: int = maxlen
        self._strategy: OverflowStrategy = strategy
        self._buffer: List[Optional[T]] = [None] * maxlen
        self._head: int = 0  # Index of the first element
        self._tail: int = 0  # Index where the next element will be appended
        self._size: int = 0

    @property
    def maxlen(self) -> int:
        """The maximum number of elements the deque can hold."""
        return self._maxlen

    @property
    def strategy(self) -> OverflowStrategy:
        """The overflow strategy used by this deque."""
        return self._strategy

    def __len__(self) -> int:
        """Return the number of elements currently in the deque."""
        return self._size

    def is_full(self) -> bool:
        """Return True if the deque is full."""
        return self._size == self._maxlen

    def is_empty(self) -> bool:
        """Return True if the deque is empty."""
        return self._size == 0

    def append(self, item: T) -> None:
        """
        Add an element to the right side of the deque.

        If the deque is full, behavior depends on the overflow strategy.
        """
        if self.is_full():
            if self._strategy == OverflowStrategy.ERROR:
                raise Full("Deque is full")
            elif self._strategy == OverflowStrategy.DISCARD:
                return
            else: # OVERWRITE
                # Overwrite oldest (at head)
                self._head = (self._head + 1) % self._maxlen
                self._size -= 1

        self._buffer[self._tail] = item
        self._tail = (self._tail + 1) % self._maxlen
        self._size += 1

    def appendleft(self, item: T) -> None:
        """
        Add an element to the left side of the deque.

        If the deque is full, behavior depends on the overflow strategy.
        """
        if self.is_full():
            if self._strategy == OverflowStrategy.ERROR:
                raise Full("Deque is full")
            elif self._strategy == OverflowStrategy.DISCARD:
                return
            else: # OVERWRITE
                # Overwrite newest at the other end (at tail-1)
                self._tail = (self._tail - 1) % self._maxlen
                self._size -= 1

        self._head = (self._head - 1) % self._maxlen
        self._buffer[self._head] = item
        self._size += 1

    def pop(self) -> T:
        """
        Remove and return an element from the right side of the deque.

        Raises:
            Empty: If the deque is empty.
        """
        if self.is_empty():
            raise Empty("pop from empty deque")
        self._tail = (self._tail - 1) % self._maxlen
        item = self._buffer[self._tail]
        self._buffer[self._tail] = None  # Clear reference
        self._size -= 1
        return item # type: ignore

    def popleft(self) -> T:
        """
        Remove and return an element from the left side of the deque.

        Raises:
            Empty: If the deque is empty.
        """
        if self.is_empty():
            raise Empty("pop from empty deque")
        item = self._buffer[self._head]
        self._buffer[self._head] = None  # Clear reference
        self._head = (self._head + 1) % self._maxlen
        self._size -= 1
        return item # type: ignore

    def peek(self) -> T:
        """
        Return the element at the right side of the deque without removing it.

        Raises:
            Empty: If the deque is empty.
        """
        if self.is_empty():
            raise Empty("peek from empty deque")
        return self._buffer[(self._tail - 1) % self._maxlen] # type: ignore

    def peekleft(self) -> T:
        """
        Return the element at the left side of the deque without removing it.

        Raises:
            Empty: If the deque is empty.
        """
        if self.is_empty():
            raise Empty("peek from empty deque")
        return self._buffer[self._head] # type: ignore

    def __iter__(self) -> Iterator[T]:
        """Return an iterator over the elements in the deque from left to right."""
        for i in range(self._size):
            yield self._buffer[(self._head + i) % self._maxlen] # type: ignore

    def __repr__(self) -> str:
        items = list(self)
        return f"{self.__class__.__name__}({items}, maxlen={self._maxlen}, strategy={self._strategy})"

    @classmethod
    def from_iterable(cls, iterable: Iterable[T], maxlen: int, strategy: OverflowStrategy = OverflowStrategy.OVERWRITE) -> 'RingDeque[T]':
        """Create a RingDeque from an iterable."""
        dq = cls(maxlen, strategy)
        for item in iterable:
            dq.append(item)
        return dq


class ThreadSafeRingDeque(RingDeque[T]):
    """
    A thread-safe version of RingDeque using a lock.
    """
    def __init__(self, maxlen: int, strategy: OverflowStrategy = OverflowStrategy.OVERWRITE) -> None:
        super().__init__(maxlen, strategy)
        self._lock = threading.RLock()

    def append(self, item: T) -> None:
        with self._lock:
            # Call RingDeque.append directly to avoid super() overhead in subclasses
            RingDeque.append(self, item)

    def appendleft(self, item: T) -> None:
        with self._lock:
            RingDeque.appendleft(self, item)

    def pop(self) -> T:
        with self._lock:
            return RingDeque.pop(self)

    def popleft(self) -> T:
        with self._lock:
            return RingDeque.popleft(self)

    def peek(self) -> T:
        with self._lock:
            return RingDeque.peek(self)

    def peekleft(self) -> T:
        with self._lock:
            return RingDeque.peekleft(self)

    def __len__(self) -> int:
        with self._lock:
            return RingDeque.__len__(self)

    def is_full(self) -> bool:
        with self._lock:
            return RingDeque.is_full(self)

    def is_empty(self) -> bool:
        with self._lock:
            return RingDeque.is_empty(self)

    def __iter__(self) -> Iterator[T]:
        with self._lock:
            # Snapshot to be thread-safe during iteration
            return iter(list(RingDeque.__iter__(self)))


class BlockingRingDeque(ThreadSafeRingDeque[T]):
    """
    A thread-safe version of RingDeque with blocking put and get operations.

    The 'put' method blocks if the deque is full, UNLESS strategy is OVERWRITE.
    If strategy is OVERWRITE, 'put' will behave like 'append' and not block.
    """
    def __init__(self, maxlen: int, strategy: OverflowStrategy = OverflowStrategy.OVERWRITE) -> None:
        super().__init__(maxlen, strategy)
        self._not_empty = threading.Condition(self._lock)
        self._not_full = threading.Condition(self._lock)

    def append(self, item: T) -> None:
        with self._lock:
            RingDeque.append(self, item)
            self._not_empty.notify()

    def appendleft(self, item: T) -> None:
        with self._lock:
            RingDeque.appendleft(self, item)
            self._not_empty.notify()

    def pop(self) -> T:
        with self._lock:
            item = RingDeque.pop(self)
            self._not_full.notify()
            return item

    def popleft(self) -> T:
        with self._lock:
            item = RingDeque.popleft(self)
            self._not_full.notify()
            return item

    def put(self, item: T, block: bool = True, timeout: Optional[float] = None) -> None:
        """
        Add an item to the right of the deque.
        If block is True and deque is full (and strategy is NOT OVERWRITE), wait up to timeout seconds.

        Raises:
            Full: If deque is full and cannot be added (timeout or non-blocking).
        """
        with self._lock:
            if RingDeque.is_full(self) and self._strategy != OverflowStrategy.OVERWRITE:
                if not block:
                    raise Full("Deque is full")

                if timeout is None:
                    while RingDeque.is_full(self):
                        self._not_full.wait()
                elif timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    endtime = time.time() + timeout
                    while RingDeque.is_full(self):
                        remaining = endtime - time.time()
                        if remaining <= 0.0:
                            raise Full("Deque is full (timeout)")
                        self._not_full.wait(remaining)

            # Now we can append. If it was OVERWRITE, it would have worked anyway.
            # If it was ERROR/DISCARD, we waited until there was space.
            RingDeque.append(self, item)
            self._not_empty.notify()

    def get(self, block: bool = True, timeout: Optional[float] = None) -> T:
        """
        Remove and return an item from the left of the deque.
        If block is True and deque is empty, wait up to timeout seconds.

        Raises:
            Empty: If deque is empty and timeout expires or block is False.
        """
        with self._lock:
            if RingDeque.is_empty(self):
                if not block:
                    raise Empty("Deque is empty")

                if timeout is None:
                    while RingDeque.is_empty(self):
                        self._not_empty.wait()
                elif timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    endtime = time.time() + timeout
                    while RingDeque.is_empty(self):
                        remaining = endtime - time.time()
                        if remaining <= 0.0:
                            raise Empty("Deque is empty (timeout)")
                        self._not_empty.wait(remaining)

            item = RingDeque.popleft(self)
            self._not_full.notify()
            return item
