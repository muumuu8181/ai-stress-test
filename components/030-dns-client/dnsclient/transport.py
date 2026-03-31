import socket
import struct
from .protocol import DNSPacket


class DNSTransportError(Exception):
    """Exception raised for DNS transport errors."""

    pass


def query_udp(data: bytes, server: str, port: int = 53, timeout: float = 5.0) -> bytes:
    """Sends a DNS query over UDP and returns the response bytes."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout)
        try:
            sock.sendto(data, (server, port))
            response, _ = sock.recvfrom(4096)
            return response
        except socket.timeout:
            raise DNSTransportError(f"UDP query to {server}:{port} timed out")
        except Exception as e:
            raise DNSTransportError(f"UDP query failed: {e}")


def query_tcp(data: bytes, server: str, port: int = 53, timeout: float = 5.0) -> bytes:
    """Sends a DNS query over TCP and returns the response bytes."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            sock.connect((server, port))
            # In TCP, the query is preceded by a 2-byte length field
            length = len(data)
            sock.sendall(struct.pack("!H", length) + data)

            # Read the 2-byte length field from the response
            resp_len_data = sock.recv(2)
            if len(resp_len_data) < 2:
                raise DNSTransportError("Failed to read TCP response length")
            resp_len = struct.unpack("!H", resp_len_data)[0]

            # Read the actual response
            response = b""
            while len(response) < resp_len:
                chunk = sock.recv(resp_len - len(response))
                if not chunk:
                    break
                response += chunk

            if len(response) < resp_len:
                raise DNSTransportError("Incomplete TCP response")
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
