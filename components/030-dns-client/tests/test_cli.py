import unittest.mock as mock
from io import StringIO
import sys
from dnsclient.cli import main, print_packet, format_rr
from dnsclient.protocol import (
    DNSPacket,
    DNSHeader,
    DNSQuestion,
    DNSResourceRecord,
    DNSType,
)


def test_format_rr():
    rr = DNSResourceRecord("example.com", DNSType.A, 1, 3600, 4, "1.2.3.4")
    formatted = format_rr(rr)
    assert "example.com" in formatted
    assert "3600" in formatted
    assert "A" in formatted
    assert "1.2.3.4" in formatted


def test_print_packet():
    h = DNSHeader(id=1234, qr=1, ancount=1)
    q = DNSQuestion("example.com", DNSType.A)
    ans = DNSResourceRecord("example.com", DNSType.A, 1, 3600, 4, "1.2.3.4")
    packet = DNSPacket(h, [q], answers=[ans])

    with mock.patch("sys.stdout", new=StringIO()) as fake_out:
        print_packet(packet)
        output = fake_out.getvalue()
        assert ";; QUESTION SECTION:" in output
        assert ";; ANSWER SECTION:" in output
        assert "example.com" in output
        assert "1.2.3.4" in output


@mock.patch("dnsclient.resolver.DNSResolver.resolve")
def test_main_cli(mock_resolve):
    h = DNSHeader(id=1, qr=1, ancount=1)
    q = DNSQuestion("example.com", DNSType.A)
    ans = DNSResourceRecord("example.com", DNSType.A, 1, 3600, 4, "1.2.3.4")
    packet = DNSPacket(h, [q], answers=[ans])
    mock_resolve.return_value = packet

    # Simulate CLI arguments
    with mock.patch("sys.argv", ["dnsclient", "example.com", "A"]):
        with mock.patch("sys.stdout", new=StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            assert "1.2.3.4" in output
            assert ";; Query time:" in output


@mock.patch("dnsclient.resolver.DNSResolver.resolve")
def test_main_cli_trace(mock_resolve):
    h = DNSHeader(id=1, qr=1, ancount=1)
    q = DNSQuestion("example.com", DNSType.A)
    ans = DNSResourceRecord("example.com", DNSType.A, 1, 3600, 4, "1.2.3.4")
    packet = DNSPacket(h, [q], answers=[ans])
    mock_resolve.return_value = packet

    with mock.patch("sys.argv", ["dnsclient", "example.com", "A", "--trace"]):
        with mock.patch("sys.stdout", new=StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            assert ";; RESOLUTION TRACE:" in output
            assert "1.2.3.4" in output
