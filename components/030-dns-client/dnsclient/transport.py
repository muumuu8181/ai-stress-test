import socket
import struct
from .protocol import DNSPacket


class DNSTransportError(Exception):
    """Exception raised for DNS transport errors."""

    pass


def _recv_exactly(sock: socket.socket, n: int) -> bytes:
    """Helper to receive exactly n bytes from a TCP socket."""
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise DNSTransportError("Connection closed while receiving data")
        data += chunk
    return data


def query_udp(data: bytes, server: str, port: int = 53, timeout: float = 5.0) -> bytes:
    """Sends a DNS query over UDP and returns the response bytes."""
    addr_info = socket.getaddrinfo(server, port, type=socket.SOCK_DGRAM)
    if not addr_info:
        raise DNSTransportError(f"Could not resolve server: {server}")

    family, socktype, proto, canonname, sockaddr = addr_info[0]

    with socket.socket(family, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout)
        try:
            sock.sendto(data, sockaddr)
            response, _ = sock.recvfrom(4096)
            return response
        except socket.timeout:
            raise DNSTransportError(f"UDP query to {server}:{port} timed out")
        except Exception as e:
            raise DNSTransportError(f"UDP query failed: {e}")


def query_tcp(data: bytes, server: str, port: int = 53, timeout: float = 5.0) -> bytes:
    """Sends a DNS query over TCP and returns the response bytes."""
    addr_info = socket.getaddrinfo(server, port, type=socket.SOCK_STREAM)
    if not addr_info:
        raise DNSTransportError(f"Could not resolve server: {server}")

    family, socktype, proto, canonname, sockaddr = addr_info[0]

    with socket.socket(family, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            sock.connect(sockaddr)
            # In TCP, the query is preceded by a 2-byte length field
            length = len(data)
            sock.sendall(struct.pack("!H", length) + data)

            # Read the 2-byte length field from the response using the helper
            resp_len_data = _recv_exactly(sock, 2)
            resp_len = struct.unpack("!H", resp_len_data)[0]

            # Read exactly resp_len bytes
            response = _recv_exactly(sock, resp_len)
            return response
        except socket.timeout:
            raise DNSTransportError(f"TCP query to {server}:{port} timed out")
        except Exception as e:
            raise DNSTransportError(f"TCP query failed: {e}")


def send_query(
    packet: DNSPacket, server: str, use_tcp: bool = False, timeout: float = 5.0
) -> DNSPacket:
    """Packs a DNSPacket and sends it to the specified server."""
    data = packet.pack()
    if use_tcp:
        resp_data = query_tcp(data, server, timeout=timeout)
    else:
        resp_data = query_udp(data, server, timeout=timeout)

    return DNSPacket.unpack(resp_data)
