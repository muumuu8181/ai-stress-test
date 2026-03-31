import io
import struct
import pytest
from dnsclient.protocol import (
    DNSHeader,
    DNSQuestion,
    DNSResourceRecord,
    DNSPacket,
    DNSType,
    encode_dns_name,
    decode_dns_name,
)


def test_encode_dns_name():
    assert encode_dns_name("example.com") == b"\x07example\x03com\x00"
    assert encode_dns_name(".") == b"\x00"
    assert encode_dns_name("") == b"\x00"


def test_decode_dns_name():
    data = b"\x07example\x03com\x00"
    reader = io.BytesIO(data)
    assert decode_dns_name(reader, data) == "example.com"


def test_decode_dns_name_compression():
    # example.com at offset 0
    # foo.example.com at offset 13
    data = b"\x07example\x03com\x00\x03foo\xc0\x00"
    reader = io.BytesIO(data)
    reader.seek(13)
    assert decode_dns_name(reader, data) == "foo.example.com"


def test_dns_header_pack_unpack():
    h = DNSHeader(
        id=0x1234,
        qr=1,
        opcode=0,
        aa=1,
        tc=0,
        rd=1,
        ra=1,
        z=0,
        rcode=0,
        qdcount=1,
        ancount=1,
    )
    packed = h.pack()
    assert len(packed) == 12

    h2 = DNSHeader.unpack(packed)
    assert h2.id == 0x1234
    assert h2.qr == 1
    assert h2.aa == 1
    assert h2.rd == 1
    assert h2.ra == 1
    assert h2.qdcount == 1
    assert h2.ancount == 1


def test_dns_question_pack_unpack():
    q = DNSQuestion("example.com", DNSType.A)
    packed = q.pack()
    reader = io.BytesIO(packed)
    q2 = DNSQuestion.unpack(reader, packed)
    assert q2.qname == "example.com"
    assert q2.qtype == DNSType.A


def test_dns_rr_unpack_a():
    # Name: example.com (offset 0), Type: A, Class: IN, TTL: 3600, RDLen: 4, RData: 1.2.3.4
    data = (
        b"\x07example\x03com\x00"
        + struct.pack("!HHIH", DNSType.A, 1, 3600, 4)
        + b"\x01\x02\x03\x04"
    )
    reader = io.BytesIO(data)
    rr = DNSResourceRecord.unpack(reader, data)
    assert rr.name == "example.com"
    assert rr.type == DNSType.A
    assert rr.ttl == 3600
    assert rr.rdata == "1.2.3.4"


def test_dns_rr_unpack_aaaa():
    # IPv6: 2001:db8::1
    ip_bytes = b"\x20\x01\x0d\xb8" + b"\x00" * 10 + b"\x00\x01"
    data = (
        b"\x07example\x03com\x00"
        + struct.pack("!HHIH", DNSType.AAAA, 1, 3600, 16)
        + ip_bytes
    )
    reader = io.BytesIO(data)
    rr = DNSResourceRecord.unpack(reader, data)
    assert rr.type == DNSType.AAAA
    assert rr.rdata == "2001:db8::1"


def test_dns_rr_unpack_mx():
    # Preference: 10, Exchange: mail.example.com
    mx_data = struct.pack("!H", 10) + b"\x04mail\xc0\x00"
    # example.com at 0, mail.example.com at 13
    full_data = b"\x07example\x03com\x00" + b"\x04mail\xc0\x00"

    # RR starts at some dummy position
    rr_header = b"\x07example\x03com\x00" + struct.pack(
        "!HHIH", DNSType.MX, 1, 3600, len(mx_data)
    )
    reader = io.BytesIO(rr_header + mx_data)
    rr = DNSResourceRecord.unpack(reader, rr_header + mx_data)
    assert rr.type == DNSType.MX
    assert rr.rdata["preference"] == 10
    assert rr.rdata["exchange"] == "mail.example.com"


def test_dns_rr_unpack_txt():
    txt_data = b"\x05hello\x05world"
    data = (
        b"\x07example\x03com\x00"
        + struct.pack("!HHIH", DNSType.TXT, 1, 3600, len(txt_data))
        + txt_data
    )
    reader = io.BytesIO(data)
    rr = DNSResourceRecord.unpack(reader, data)
    assert rr.type == DNSType.TXT
    assert rr.rdata == ["hello", "world"]


def test_dns_rr_unpack_soa():
    # mname: ns1.example.com, rname: admin.example.com, serial: 1, refresh: 3600, retry: 600, expire: 86400, minimum: 3600
    soa_payload = (
        b"\x03ns1\xc0\x00"
        + b"\x05admin\xc0\x00"
        + struct.pack("!IIIII", 1, 3600, 600, 86400, 3600)
    )
    full_data = b"\x07example\x03com\x00" + b"\x03ns1\xc0\x00" + b"\x05admin\xc0\x00"

    rr_header = b"\x07example\x03com\x00" + struct.pack(
        "!HHIH", DNSType.SOA, 1, 3600, len(soa_payload)
    )
    reader = io.BytesIO(rr_header + soa_payload)
    rr = DNSResourceRecord.unpack(reader, rr_header + soa_payload)
    assert rr.type == DNSType.SOA
    assert rr.rdata["mname"] == "ns1.example.com"
    assert rr.rdata["rname"] == "admin.example.com"
    assert rr.rdata["serial"] == 1
