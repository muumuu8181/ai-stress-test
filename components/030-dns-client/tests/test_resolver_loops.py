import unittest.mock as mock
import pytest
from dnsclient.resolver import DNSResolver
from dnsclient.protocol import (
    DNSPacket,
    DNSHeader,
    DNSQuestion,
    DNSResourceRecord,
    DNSType,
)


@mock.patch("dnsclient.resolver.send_query")
def test_resolver_cname_loop(mock_send):
    # a.com CNAME b.com
    # b.com CNAME a.com

    h1 = DNSHeader(id=1, qr=1, ancount=1)
    q1 = DNSQuestion("a.com", DNSType.A)
    ans1 = DNSResourceRecord("a.com", DNSType.CNAME, 1, 3600, 4, "b.com")
    resp1 = DNSPacket(h1, [q1], answers=[ans1])

    h2 = DNSHeader(id=2, qr=1, ancount=1)
    q2 = DNSQuestion("b.com", DNSType.A)
    ans2 = DNSResourceRecord("b.com", DNSType.CNAME, 1, 3600, 4, "a.com")
    resp2 = DNSPacket(h2, [q2], answers=[ans2])

    mock_send.side_effect = [resp1, resp2] * 10

    resolver = DNSResolver()
    with pytest.raises(Exception, match="CNAME chasing depth exceeded"):
        resolver.resolve("a.com", DNSType.A)


@mock.patch("dnsclient.resolver.send_query")
@mock.patch("dnsclient.transport.query_udp")
def test_resolver_ptr_cache_normalization(mock_udp, mock_send):
    # Test that PTR query for "8.8.8.8" is cached as "8.8.8.8.in-addr.arpa"

    h = DNSHeader(id=1, qr=1, ancount=1)
    q = DNSQuestion("8.8.8.8.in-addr.arpa", DNSType.PTR)
    ans = DNSResourceRecord(
        "8.8.8.8.in-addr.arpa", DNSType.PTR, 1, 3600, 4, "dns.google"
    )
    packet = DNSPacket(h, [q], answers=[ans])
    mock_send.return_value = packet

    resolver = DNSResolver()
    # 1st call: resolution
    resolver.resolve("8.8.8.8", DNSType.PTR)
    assert mock_send.call_count == 1

    # 2nd call: should be from cache
    resolver.resolve("8.8.8.8", DNSType.PTR)
    assert mock_send.call_count == 1
