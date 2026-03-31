# Rate Limiter

A thread-safe Python implementation of common rate-limiting algorithms: Token Bucket and Sliding Window (Log).

## Features

- **Token Bucket**: Allows for bursts of traffic while maintaining a steady average rate.
- **Sliding Window Log**: Precisely limits the number of requests in a sliding time window.
- **Thread-Safe**: Uses `threading.Lock` to ensure safety in multi-threaded environments.
- **Type-Hinted**: Full TypeScript-style type hints for Python.
- **Comprehensive Tests**: Unit tests, integration tests, and edge case handling.

## Installation

No external dependencies are required. Just ensure you have Python 3.7+ installed.

## Usage

### Token Bucket

```python
from rate_limiter.token_bucket import TokenBucketRateLimiter

# Capacity of 5 tokens, refills at 1 token per second
limiter = TokenBucketRateLimiter(capacity=5, refill_rate=1)

if limiter.allow_request():
    print("Request allowed")
else:
    print("Rate limited")
```

### Sliding Window

```python
from rate_limiter.sliding_window import SlidingWindowRateLimiter

# Maximum 10 requests allowed within a 60-second window
limiter = SlidingWindowRateLimiter(max_requests=10, window_seconds=60)

if limiter.allow_request():
    print("Request allowed")
else:
    print("Rate limited")
```

## Running the REPL

You can interactively test the rate limiters using the provided CLI:

```bash
cd components/032-rate-limiter
PYTHONPATH=src python -m rate_limiter.cli
```

## Testing

Run the tests using `pytest`:

```bash
cd components/032-rate-limiter
PYTHONPATH=src pytest tests/test_rate_limiters.py
```

To check coverage:

```bash
cd components/032-rate-limiter
PYTHONPATH=src python -m pytest --cov=src tests/test_rate_limiters.py
```
