import time
from dnsclient.cache import DNSCache
from dnsclient.protocol import DNSResourceRecord, DNSType


def test_cache_add_get():
    cache = DNSCache()
    rr = DNSResourceRecord("example.com", DNSType.A, 1, 3600, 4, "1.2.3.4")
    cache.add(rr)

    results = cache.get("example.com", DNSType.A)
    assert results is not None
    assert len(results) == 1
    assert results[0].rdata == "1.2.3.4"


def test_cache_expiration():
    cache = DNSCache()
    # TTL: 1 sec
    rr = DNSResourceRecord("example.com", DNSType.A, 1, 1, 4, "1.2.3.4")
    cache.add(rr)

    # Still valid
    assert len(cache.get("example.com", DNSType.A)) == 1

    # Wait for expiration
    time.sleep(1.1)
    assert cache.get("example.com", DNSType.A) is None


def test_cache_clear():
    cache = DNSCache()
    rr = DNSResourceRecord("example.com", DNSType.A, 1, 3600, 4, "1.2.3.4")
    cache.add(rr)
    cache.clear()
    assert cache.get("example.com", DNSType.A) is None


def test_cache_case_insensitivity():
    cache = DNSCache()
    rr = DNSResourceRecord("EXAMPLE.COM", DNSType.A, 1, 3600, 4, "1.2.3.4")
    cache.add(rr)
    assert len(cache.get("example.com", DNSType.A)) == 1
