import unittest.mock as mock
from dnsclient.resolver import DNSResolver, ResolutionTrace
from dnsclient.protocol import (
    DNSPacket,
    DNSHeader,
    DNSQuestion,
    DNSResourceRecord,
    DNSType,
)


@mock.patch("dnsclient.resolver.send_query")
def test_resolver_direct_answer(mock_send):
    # Mock response from root that gives direct answer
    header = DNSHeader(id=1, qr=1, ancount=1)
    question = DNSQuestion("example.com", DNSType.A)
    answer = DNSResourceRecord("example.com", DNSType.A, 1, 3600, 4, "1.2.3.4")
    packet = DNSPacket(header, [question], answers=[answer])
    mock_send.return_value = packet

    resolver = DNSResolver()
    response = resolver.resolve("example.com", DNSType.A)

    assert response.answers[0].rdata == "1.2.3.4"
    assert mock_send.called


@mock.patch("dnsclient.resolver.send_query")
def test_resolver_recursive(mock_send):
    # 1st call (Root): Referral to TLD
    header1 = DNSHeader(id=1, qr=1, nscount=1, arcount=1)
    q1 = DNSQuestion("example.com", DNSType.A)
    ns1 = DNSResourceRecord("com", DNSType.NS, 1, 3600, 4, "ns.tld.com")
    glue1 = DNSResourceRecord("ns.tld.com", DNSType.A, 1, 3600, 4, "1.1.1.1")
    resp1 = DNSPacket(header1, [q1], authorities=[ns1], additionals=[glue1])

    # 2nd call (TLD): Direct answer
    header2 = DNSHeader(id=2, qr=1, ancount=1)
    ans2 = DNSResourceRecord("example.com", DNSType.A, 1, 3600, 4, "2.2.2.2")
    resp2 = DNSPacket(header2, [q1], answers=[ans2])

    mock_send.side_effect = [resp1, resp2]

    resolver = DNSResolver()
    trace = ResolutionTrace()
    response = resolver.resolve("example.com", DNSType.A, trace=trace)

    assert response.answers[0].rdata == "2.2.2.2"
    assert len(trace.steps) == 2
    assert trace.steps[0]["server"] in [
        "198.41.0.4",
        "199.9.14.201",
        "192.33.4.12",
        "199.7.91.13",
        "192.203.230.10",
        "192.5.5.241",
        "192.112.36.4",
        "198.97.190.53",
        "192.36.148.17",
        "192.58.128.30",
        "193.0.14.129",
        "199.7.83.42",
        "202.12.27.33",
    ]
    assert trace.steps[1]["server"] == "1.1.1.1"


def test_ptr_formatting():
    resolver = DNSResolver()
    with mock.patch.object(resolver, "_resolve_recursive") as mock_recursive:
        resolver.resolve("8.8.8.8", DNSType.PTR)
        # Check if the name was converted correctly for PTR
        mock_recursive.assert_called_once()
        args = mock_recursive.call_args[0]
        assert args[0] == "8.8.8.8.in-addr.arpa"
