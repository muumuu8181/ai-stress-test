import pytest
import threading
import time
from ring_buffer.deque import RingDeque, ThreadSafeRingDeque, BlockingRingDeque, OverflowStrategy, Full, Empty

def test_ring_deque_basic():
    dq = RingDeque(maxlen=3)
    assert dq.maxlen == 3
    assert len(dq) == 0
    assert dq.is_empty()
    assert not dq.is_full()

    dq.append(1)
    dq.append(2)
    assert len(dq) == 2
    assert list(dq) == [1, 2]

    assert dq.popleft() == 1
    assert len(dq) == 1
    assert list(dq) == [2]

    dq.appendleft(0)
    assert list(dq) == [0, 2]

    assert dq.pop() == 2
    assert list(dq) == [0]
    assert dq.pop() == 0
    assert dq.is_empty()

def test_ring_deque_overflow_overwrite():
    dq = RingDeque(maxlen=3, strategy=OverflowStrategy.OVERWRITE)
    dq.append(1)
    dq.append(2)
    dq.append(3)
    assert dq.is_full()

    dq.append(4) # Should overwrite 1
    assert list(dq) == [2, 3, 4]

    dq.appendleft(0) # Should overwrite 4
    assert list(dq) == [0, 2, 3]

def test_ring_deque_overflow_error():
    dq = RingDeque(maxlen=2, strategy=OverflowStrategy.ERROR)
    dq.append(1)
    dq.append(2)
    with pytest.raises(Full):
        dq.append(3)
    with pytest.raises(Full):
        dq.appendleft(0)

def test_ring_deque_overflow_discard():
    dq = RingDeque(maxlen=2, strategy=OverflowStrategy.DISCARD)
    dq.append(1)
    dq.append(2)
    dq.append(3) # Should be discarded
    assert list(dq) == [1, 2]
    dq.appendleft(0) # Should be discarded
    assert list(dq) == [1, 2]

def test_ring_deque_peek():
    dq = RingDeque(maxlen=3)
    with pytest.raises(Empty):
        dq.peek()
    with pytest.raises(Empty):
        dq.peekleft()

    dq.append(1)
    dq.append(2)
    assert dq.peek() == 2
    assert dq.peekleft() == 1
    assert len(dq) == 2

def test_ring_deque_from_iterable():
    dq = RingDeque.from_iterable([1, 2, 3, 4], maxlen=3)
    assert list(dq) == [2, 3, 4]

def test_thread_safe_ring_deque():
    dq = ThreadSafeRingDeque(maxlen=1000)

    def producer():
        for i in range(500):
            dq.append(i)

    def consumer():
        for i in range(500):
            dq.appendleft(i)

    t1 = threading.Thread(target=producer)
    t2 = threading.Thread(target=consumer)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert len(dq) == 1000

def test_blocking_ring_deque_put_get():
    dq = BlockingRingDeque(maxlen=2, strategy=OverflowStrategy.ERROR)

    results = []
    def consumer():
        results.append(dq.get())
        results.append(dq.get())
        results.append(dq.get())

    t = threading.Thread(target=consumer)
    t.start()

    time.sleep(0.1)
    dq.put(1)
    dq.put(2)
    dq.put(3)

    t.join()
    assert results == [1, 2, 3]

def test_blocking_ring_deque_timeout():
    dq = BlockingRingDeque(maxlen=1, strategy=OverflowStrategy.ERROR)
    dq.put(1)

    start = time.time()
    with pytest.raises(Full):
        dq.put(2, timeout=0.2)
    duration = time.time() - start
    assert 0.15 <= duration <= 0.3

    dq.get()
    with pytest.raises(Empty):
        dq.get(timeout=0.2)

def test_edge_cases():
    with pytest.raises(ValueError):
        RingDeque(maxlen=0)

    dq = RingDeque(maxlen=1)
    dq.append(1)
    assert dq.pop() == 1
    with pytest.raises(Empty):
        dq.pop()

    dq.append(2)
    dq.append(3) # Overwrite 2
    assert dq.peek() == 3
    assert dq.peekleft() == 3
