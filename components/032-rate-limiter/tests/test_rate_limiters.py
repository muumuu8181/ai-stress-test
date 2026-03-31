import time
import threading
import pytest
from rate_limiter.token_bucket import TokenBucketRateLimiter
from rate_limiter.sliding_window import SlidingWindowRateLimiter


def test_token_bucket_initial_capacity():
    limiter = TokenBucketRateLimiter(capacity=5, refill_rate=1)
    for _ in range(5):
        assert limiter.allow_request() is True
    assert limiter.allow_request() is False


def test_token_bucket_refill():
    limiter = TokenBucketRateLimiter(capacity=1, refill_rate=10)
    assert limiter.allow_request() is True
    assert limiter.allow_request() is False
    time.sleep(0.11)  # Enough time to refill 1 token
    assert limiter.allow_request() is True


def test_token_bucket_thread_safety():
    limiter = TokenBucketRateLimiter(capacity=100, refill_rate=0)
    results = []
    results_lock = threading.Lock()

    def make_requests():
        for _ in range(10):
            res = limiter.allow_request()
            with results_lock:
                results.append(res)

    threads = [threading.Thread(target=make_requests) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert all(results)
    assert len(results) == 100
    assert limiter.allow_request() is False


def test_sliding_window_max_requests():
    limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=1)
    for _ in range(5):
        assert limiter.allow_request() is True
    assert limiter.allow_request() is False


def test_sliding_window_cleanup():
    limiter = SlidingWindowRateLimiter(max_requests=1, window_seconds=0.1)
    assert limiter.allow_request() is True
    assert limiter.allow_request() is False
    time.sleep(0.11)
    assert limiter.allow_request() is True


def test_sliding_window_thread_safety():
    limiter = SlidingWindowRateLimiter(max_requests=100, window_seconds=10)
    results = []
    results_lock = threading.Lock()

    def make_requests():
        for _ in range(10):
            res = limiter.allow_request()
            with results_lock:
                results.append(res)

    threads = [threading.Thread(target=make_requests) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert all(results)
    assert len(results) == 100
    assert limiter.allow_request() is False


def test_token_bucket_zero_capacity():
    limiter = TokenBucketRateLimiter(capacity=0, refill_rate=10)
    assert limiter.allow_request() is False


def test_sliding_window_zero_requests():
    limiter = SlidingWindowRateLimiter(max_requests=0, window_seconds=10)
    assert limiter.allow_request() is False


def test_token_bucket_negative_capacity():
    with pytest.raises(ValueError):
        TokenBucketRateLimiter(capacity=-1, refill_rate=10)


def test_token_bucket_negative_refill_rate():
    with pytest.raises(ValueError):
        TokenBucketRateLimiter(capacity=10, refill_rate=-1)


def test_sliding_window_negative_requests():
    with pytest.raises(ValueError):
        SlidingWindowRateLimiter(max_requests=-1, window_seconds=10)


def test_sliding_window_invalid_window():
    with pytest.raises(ValueError):
        SlidingWindowRateLimiter(max_requests=10, window_seconds=0)
    with pytest.raises(ValueError):
        SlidingWindowRateLimiter(max_requests=10, window_seconds=-1)
