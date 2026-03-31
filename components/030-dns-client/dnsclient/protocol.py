import struct
import io
import socket
from typing import List, Optional, Any


class DNSType:
    A = 1
    NS = 2
    CNAME = 5
    SOA = 6
    PTR = 12
    MX = 15
    TXT = 16
    AAAA = 28

    _NAME_TO_TYPE = {
        "A": A,
        "NS": NS,
        "CNAME": CNAME,
        "SOA": SOA,
        "PTR": PTR,
        "MX": MX,
        "TXT": TXT,
        "AAAA": AAAA,
    }

    _TYPE_TO_NAME = {v: k for k, v in _NAME_TO_TYPE.items()}

    @classmethod
    def from_string(cls, name: str) -> int:
        """Converts a string record type to its integer value."""
        return cls._NAME_TO_TYPE.get(name.upper(), 0)

    @classmethod
    def to_string(cls, value: int) -> str:
        """Converts an integer record type to its string name."""
        return cls._TYPE_TO_NAME.get(value, f"TYPE{value}")


class DNSClass:
    IN = 1


class DNSHeader:
    """Represents a DNS packet header."""

    def __init__(
        self,
        id: int,
        qr: int = 0,
        opcode: int = 0,
        aa: int = 0,
        tc: int = 0,
        rd: int = 1,
        ra: int = 0,
        z: int = 0,
        rcode: int = 0,
        qdcount: int = 0,
        ancount: int = 0,
        nscount: int = 0,
        arcount: int = 0,
    ) -> None:
        self.id = id
        self.qr = qr
        self.opcode = opcode
        self.aa = aa
        self.tc = tc
        self.rd = rd
        self.ra = ra
        self.z = z
        self.rcode = rcode
        self.qdcount = qdcount
        self.ancount = ancount
        self.nscount = nscount
        self.arcount = arcount

    def pack(self) -> bytes:
        """Packs the header into bytes."""
        flags = (
            (self.qr << 15)
            | (self.opcode << 11)
            | (self.aa << 10)
            | (self.tc << 9)
            | (self.rd << 8)
            | (self.ra << 7)
            | (self.z << 4)
            | self.rcode
        )
        return struct.pack(
            "!HHHHHH",
            self.id,
            flags,
            self.qdcount,
            self.ancount,
            self.nscount,
            self.arcount,
        )

    @classmethod
    def unpack(cls, data: bytes) -> "DNSHeader":
        """Unpacks bytes into a DNSHeader object."""
        id, flags, qdcount, ancount, nscount, arcount = struct.unpack(
            "!HHHHHH", data[:12]
        )
        qr = (flags >> 15) & 1
        opcode = (flags >> 11) & 0xF
        aa = (flags >> 10) & 1
        tc = (flags >> 9) & 1
        rd = (flags >> 8) & 1
        ra = (flags >> 7) & 1
        z = (flags >> 4) & 7
        rcode = flags & 0xF
        return cls(
            id, qr, opcode, aa, tc, rd, ra, z, rcode, qdcount, ancount, nscount, arcount
        )


def encode_dns_name(name: str) -> bytes:
    """Encodes a domain name into DNS format (e.g., \x07example\x03com\x00)."""
    if name == "." or not name:
        return b"\x00"
    parts = name.split(".")
    res = b""
    for part in parts:
        if not part:
            continue
        data = part.encode("ascii")
        res += struct.pack("!B", len(data)) + data
    res += b"\x00"
    return res


def decode_dns_name(
    reader: io.BytesIO, full_data: bytes, visited: Optional[set] = None
) -> str:
    """Decodes a domain name from DNS format, handling compression and pointer cycles."""
    if visited is None:
        visited = set()

    parts = []
    while True:
        pos = reader.tell()
        if pos in visited:
            raise ValueError("DNS name contains compression pointer cycle")
        visited.add(pos)

        length_byte = reader.read(1)
        if not length_byte:
            break
        (length,) = struct.unpack("!B", length_byte)
        if length == 0:
            break
        if (length & 0xC0) == 0xC0:
            # Compression
            (other_byte,) = struct.unpack("!B", reader.read(1))
            offset = ((length & 0x3F) << 8) | other_byte
            old_pos = reader.tell()
            reader.seek(offset)
            # Pass visited set to recursive call to detect cycles
            parts.append(decode_dns_name(reader, full_data, visited))
            reader.seek(old_pos)
            break
        else:
            parts.append(reader.read(length).decode("ascii"))

    name = ".".join(parts)
    return name if name else "."


class DNSQuestion:
    """Represents a DNS question."""

    def __init__(self, qname: str, qtype: int, qclass: int = DNSClass.IN) -> None:
        self.qname = qname
        self.qtype = qtype
        self.qclass = qclass

    def pack(self) -> bytes:
        """Packs the question into bytes."""
        return encode_dns_name(self.qname) + struct.pack("!HH", self.qtype, self.qclass)

    @classmethod
    def unpack(cls, reader: io.BytesIO, full_data: bytes) -> "DNSQuestion":
        """Unpacks a DNSQuestion from a byte stream."""
        qname = decode_dns_name(reader, full_data)
        qtype, qclass = struct.unpack("!HH", reader.read(4))
        return cls(qname, qtype, qclass)


class DNSResourceRecord:
    """Represents a DNS resource record."""

    def __init__(
        self,
        name: str,
        type: int,
        cls: int,
        ttl: int,
        rdlength: int,
        rdata: Any,
    ) -> None:
        self.name = name
        self.type = type
        self.cls = cls
        self.ttl = ttl
        self.rdlength = rdlength
        self.rdata = rdata

    @classmethod
    def unpack(cls, reader: io.BytesIO, full_data: bytes) -> "DNSResourceRecord":
        """Unpacks a DNSResourceRecord from a byte stream."""
        name = decode_dns_name(reader, full_data)
        type, r_cls, ttl, rdlength = struct.unpack("!HHIH", reader.read(10))

        start_pos = reader.tell()
        parsed_rdata: Any = None

        if type == DNSType.A:
            raw_rdata = reader.read(rdlength)
            parsed_rdata = socket.inet_ntop(socket.AF_INET, raw_rdata)
        elif type == DNSType.AAAA:
            raw_rdata = reader.read(rdlength)
            parsed_rdata = socket.inet_ntop(socket.AF_INET6, raw_rdata)
        elif type in (DNSType.NS, DNSType.CNAME, DNSType.PTR):
            parsed_rdata = decode_dns_name(reader, full_data)
        elif type == DNSType.MX:
            preference = struct.unpack("!H", reader.read(2))[0]
            exchange = decode_dns_name(reader, full_data)
            parsed_rdata = {"preference": preference, "exchange": exchange}
        elif type == DNSType.TXT:
            raw_rdata = reader.read(rdlength)
            txt_parts = []
            txt_reader = io.BytesIO(raw_rdata)
            while True:
                len_byte = txt_reader.read(1)
                if not len_byte:
                    break
                (txt_len,) = struct.unpack("!B", len_byte)
                txt_parts.append(
                    txt_reader.read(txt_len).decode("ascii", errors="replace")
                )
            parsed_rdata = txt_parts
        elif type == DNSType.SOA:
            mname = decode_dns_name(reader, full_data)
            rname = decode_dns_name(reader, full_data)
            serial, refresh, retry, expire, minimum = struct.unpack(
                "!IIIII", reader.read(20)
            )
            parsed_rdata = {
                "mname": mname,
                "rname": rname,
                "serial": serial,
                "refresh": refresh,
                "retry": retry,
                "expire": expire,
                "minimum": minimum,
            }
        else:
            # Fallback for unknown types
            parsed_rdata = reader.read(rdlength)

        # Ensure we've read exactly rdlength bytes
        end_pos = reader.tell()
        bytes_read = end_pos - start_pos
        if bytes_read < rdlength:
            reader.read(rdlength - bytes_read)

        return cls(name, type, r_cls, ttl, rdlength, parsed_rdata)

    def __repr__(self) -> str:
        return f"DNSResourceRecord(name={self.name}, type={DNSType.to_string(self.type)}, ttl={self.ttl}, rdata={self.rdata})"


class DNSPacket:
    """Represents a full DNS packet."""

    def __init__(
        self,
        header: DNSHeader,
        questions: List[DNSQuestion],
        answers: Optional[List[DNSResourceRecord]] = None,
        authorities: Optional[List[DNSResourceRecord]] = None,
        additionals: Optional[List[DNSResourceRecord]] = None,
    ) -> None:
        self.header = header
        self.questions = questions
        self.answers = answers or []
        self.authorities = authorities or []
        self.additionals = additionals or []

    def pack(self) -> bytes:
        """Packs the DNSPacket into bytes."""
        self.header.qdcount = len(self.questions)
        self.header.ancount = len(self.answers)
        self.header.nscount = len(self.authorities)
        self.header.arcount = len(self.additionals)

        res = self.header.pack()
        for q in self.questions:
            res += q.pack()
        return res

    @classmethod
    def unpack(cls, data: bytes) -> "DNSPacket":
        """Unpacks bytes into a DNSPacket."""
        reader = io.BytesIO(data)
        header = DNSHeader.unpack(reader.read(12))

        questions = []
        for _ in range(header.qdcount):
            questions.append(DNSQuestion.unpack(reader, data))

        answers = []
        for _ in range(header.ancount):
            answers.append(DNSResourceRecord.unpack(reader, data))

        authorities = []
        for _ in range(header.nscount):
            authorities.append(DNSResourceRecord.unpack(reader, data))

        additionals = []
        for _ in range(header.arcount):
            additionals.append(DNSResourceRecord.unpack(reader, data))

        return cls(header, questions, answers, authorities, additionals)
