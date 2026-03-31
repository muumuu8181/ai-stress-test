import base64
import hashlib
from typing import Dict, Optional, Tuple

GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

class HandshakeError(Exception):
    """Exception raised for errors during the WebSocket handshake."""
    pass

def parse_http_headers(raw_request: bytes) -> Dict[str, str]:
    """
    Parses raw HTTP request bytes and returns a dictionary of headers.

    Args:
        raw_request: The raw bytes of the HTTP request.

    Returns:
        A dictionary of header names and values (lowercase names).
    """
    if not raw_request:
        raise HandshakeError("Empty request")
    try:
        decoded = raw_request.decode("utf-8")
        if "\r\n" not in decoded:
            raise HandshakeError("Invalid HTTP request format")
        request_line, *header_lines = decoded.split("\r\n")
        headers = {}
        for line in header_lines:
            if not line:
                break
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key.lower()] = value
        return headers
    except Exception as e:
        raise HandshakeError(f"Failed to parse HTTP headers: {e}")

def generate_accept_key(sec_websocket_key: str) -> str:
    """
    Generates the Sec-WebSocket-Accept key for the handshake response.

    Args:
        sec_websocket_key: The Sec-WebSocket-Key from the client request.

    Returns:
        The base64 encoded SHA-1 hash of the key concatenated with the GUID.
    """
    concatenated = sec_websocket_key + GUID
    sha1_hash = hashlib.sha1(concatenated.encode("utf-8")).digest()
    return base64.b64encode(sha1_hash).decode("utf-8")

def validate_handshake(headers: Dict[str, str]) -> str:
    """
    Validates the handshake headers and returns the Sec-WebSocket-Key.

    Args:
        headers: The dictionary of HTTP headers.

    Returns:
        The Sec-WebSocket-Key if the handshake is valid.

    Raises:
        HandshakeError: If the handshake headers are invalid.
    """
    if headers.get("upgrade", "").lower() != "websocket":
        raise HandshakeError("Missing or invalid 'Upgrade' header")
    connection = headers.get("connection", "").lower()
    if "upgrade" not in connection:
        raise HandshakeError("Missing or invalid 'Connection' header")

    sec_key = headers.get("sec-websocket-key")
    if not sec_key:
        raise HandshakeError("Missing 'Sec-WebSocket-Key' header")

    return sec_key

def build_handshake_response(accept_key: str) -> bytes:
    """
    Builds the HTTP 101 Switching Protocols response.

    Args:
        accept_key: The generated Sec-WebSocket-Accept key.

    Returns:
        The raw bytes of the HTTP response.
    """
    response = (
        "HTTP/1.1 101 Switching Protocols\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Accept: {accept_key}\r\n"
        "\r\n"
    )
    return response.encode("utf-8")
