import unittest.mock as mock
import pytest
import io
import struct
from dnsclient.protocol import (
    DNSResourceRecord,
    DNSType,
    decode_dns_name,
    DNSPacket,
    DNSHeader,
    DNSQuestion,
)


def test_dns_rr_unpack_ns():
    # NS record
    ns_data = b"\x03ns1\x07example\x03com\x00"
    data = (
        b"\x07example\x03com\x00"
        + struct.pack("!HHIH", DNSType.NS, 1, 3600, len(ns_data))
        + ns_data
    )
    reader = io.BytesIO(data)
    rr = DNSResourceRecord.unpack(reader, data)
    assert rr.type == DNSType.NS
    assert rr.rdata == "ns1.example.com"


def test_dns_rr_unpack_cname():
    # CNAME record
    cname_data = b"\x05alias\xc0\x00"
    full_data = b"\x07example\x03com\x00\x05alias\xc0\x00"
    rr_header = b"\x07example\x03com\x00" + struct.pack(
        "!HHIH", DNSType.CNAME, 1, 3600, len(cname_data)
    )
    reader = io.BytesIO(rr_header + cname_data)
    rr = DNSResourceRecord.unpack(reader, rr_header + cname_data)
    assert rr.type == DNSType.CNAME
    assert rr.rdata == "alias.example.com"


def test_dns_rr_unpack_ptr():
    # PTR record
    ptr_data = b"\x04host\xc0\x00"
    full_data = b"\x07example\x03com\x00\x04host\xc0\x00"
    rr_header = b"\x07example\x03com\x00" + struct.pack(
        "!HHIH", DNSType.PTR, 1, 3600, len(ptr_data)
    )
    reader = io.BytesIO(rr_header + ptr_data)
    rr = DNSResourceRecord.unpack(reader, rr_header + ptr_data)
    assert rr.type == DNSType.PTR
    assert rr.rdata == "host.example.com"


def test_dns_packet_pack():
    h = DNSHeader(id=1, qdcount=1)
    q = DNSQuestion("example.com", DNSType.A)
    packet = DNSPacket(h, [q])
    packed = packet.pack()
    assert len(packed) > 12
    assert b"example" in packed


def test_dns_rr_repr():
    rr = DNSResourceRecord("example.com", DNSType.A, 1, 3600, 4, "1.2.3.4")
    assert "DNSResourceRecord" in repr(rr)
    assert "A" in repr(rr)
