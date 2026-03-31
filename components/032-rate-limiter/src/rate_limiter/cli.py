import sys
import time
from .token_bucket import TokenBucketRateLimiter
from .sliding_window import SlidingWindowRateLimiter


def main():
    print("Rate Limiter REPL")
    print("Options:")
    print("1. Token Bucket (Capacity: 5, Rate: 1/s)")
    print("2. Sliding Window (Max Requests: 5, Window: 5s)")
    print("q. Quit")

    choice = input("Select an option: ")

    if choice == '1':
        limiter = TokenBucketRateLimiter(capacity=5, refill_rate=1)
        print("Using Token Bucket Rate Limiter.")
    elif choice == '2':
        limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=5)
        print("Using Sliding Window Rate Limiter.")
    elif choice == 'q':
        sys.exit(0)
    else:
        print("Invalid choice.")
        return

    print("Type 'enter' to make a request, or 'q' to quit.")
    while True:
        cmd = input("> ")
        if cmd == 'q':
            break

        allowed = limiter.allow_request()
        if allowed:
            print(f"[{time.strftime('%H:%M:%S')}] Request allowed.")
        else:
            print(f"[{time.strftime('%H:%M:%S')}] Request rate limited.")


if __name__ == "__main__":
    main()
