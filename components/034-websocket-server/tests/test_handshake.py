import pytest
from websocket_server.handshake import (
    parse_http_headers,
    generate_accept_key,
    validate_handshake,
    build_handshake_response,
    HandshakeError,
)

def test_parse_http_headers():
    raw_request = (
        b"GET /chat HTTP/1.1\r\n"
        b"Host: server.example.com\r\n"
        b"Upgrade: websocket\r\n"
        b"Connection: Upgrade\r\n"
        b"Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
        b"Origin: http://example.com\r\n"
        b"Sec-WebSocket-Protocol: chat, superchat\r\n"
        b"Sec-WebSocket-Version: 13\r\n"
        b"\r\n"
    )
    headers = parse_http_headers(raw_request)
    assert headers["host"] == "server.example.com"
    assert headers["upgrade"] == "websocket"
    assert headers["connection"] == "Upgrade"
    assert headers["sec-websocket-key"] == "dGhlIHNhbXBsZSBub25jZQ=="

def test_parse_http_headers_invalid():
    with pytest.raises(HandshakeError):
        parse_http_headers(b"not an http request")

def test_generate_accept_key():
    key = "dGhlIHNhbXBsZSBub25jZQ=="
    expected_accept = "s3pPLMBiTxaQ9kYGzzhZRbK+xOo="
    assert generate_accept_key(key) == expected_accept

def test_validate_handshake_success():
    headers = {
        "upgrade": "websocket",
        "connection": "upgrade",
        "sec-websocket-key": "somekey"
    }
    assert validate_handshake(headers) == "somekey"

def test_validate_handshake_missing_upgrade():
    headers = {
        "connection": "Upgrade",
        "sec-websocket-key": "somekey"
    }
    with pytest.raises(HandshakeError, match="Missing or invalid 'Upgrade' header"):
        validate_handshake(headers)

def test_validate_handshake_missing_connection():
    headers = {
        "upgrade": "websocket",
        "sec-websocket-key": "somekey"
    }
    with pytest.raises(HandshakeError, match="Missing or invalid 'Connection' header"):
        validate_handshake(headers)

def test_validate_handshake_missing_key():
    headers = {
        "upgrade": "websocket",
        "connection": "upgrade"
    }
    with pytest.raises(HandshakeError, match="Missing 'Sec-WebSocket-Key' header"):
        validate_handshake(headers)

def test_build_handshake_response():
    accept_key = "s3pPLMBiTxaQ9kYGzzhZRbK+xOo="
    response = build_handshake_response(accept_key)
    assert b"HTTP/1.1 101 Switching Protocols" in response
    assert b"Upgrade: websocket" in response
    assert b"Connection: Upgrade" in response
    assert f"Sec-WebSocket-Accept: {accept_key}".encode() in response
