# DNS Client (from scratch)

A simple DNS client implemented in Python using only the standard library (and `socket` for networking).

## Features

- DNS query construction (binary packets)
- UDP/TCP query transport
- Supported record types: A, AAAA, CNAME, MX, NS, TXT, SOA, PTR
- DNS response parsing (with name compression)
- Recursive resolution (starting from root hints)
- TTL-based caching
- Reverse lookup (PTR)
- Resolution trace (dig-like output)

## Usage

### CLI

You can run the DNS client as a module:

```bash
# Basic A record query
python -m dnsclient example.com A

# MX record query with resolution trace
python -m dnsclient google.com MX --trace

# Reverse lookup (PTR)
python -m dnsclient 8.8.8.8 PTR

# Using TCP
python -m dnsclient example.com A --tcp
```

### Library

```python
from dnsclient.resolver import DNSResolver
from dnsclient.protocol import DNSType

resolver = DNSResolver()
response = resolver.resolve("example.com", DNSType.A)

for answer in response.answers:
    print(f"Name: {answer.name}, IP: {answer.rdata}")
```

## Quality Standards

- **Type Hints:** All public APIs are fully typed.
- **Documentation:** All public functions and classes have docstrings.
- **Testing:** 80%+ test coverage including unit and integration tests.

## Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=dnsclient
```

## Structure

- `dnsclient/protocol.py`: DNS packet encoding/decoding logic.
- `dnsclient/transport.py`: UDP and TCP network transport.
- `dnsclient/cache.py`: TTL-based caching.
- `dnsclient/resolver.py`: Recursive resolution logic.
- `dnsclient/cli.py`: Command-line interface.
- `tests/`: Comprehensive test suite.
