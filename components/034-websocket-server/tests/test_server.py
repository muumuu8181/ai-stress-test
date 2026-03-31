import asyncio
import pytest
import socket
from websocket_server.server import WebSocketServer, WebSocketConnection
from websocket_server.frame import encode_frame, decode_frame, Opcode

async def echo_handler(conn: WebSocketConnection, payload):
    await conn.send(payload)

@pytest.fixture
async def server():
    srv = WebSocketServer(handler=echo_handler)
    # Start server in a background task
    task = asyncio.create_task(srv.start("127.0.0.1", 0))
    # Give it a moment to start and get the port
    while not hasattr(srv, 'connections'): # Wait for initialization
        await asyncio.sleep(0.1)

    # We need to wait until the server is actually listening
    # Since start() is a serve_forever(), we can't easily get the port here
    # unless we modify start() or use a different way.
    # Let's use a fixed port for simplicity in test if 0 is hard.
    # Or better, let's use a lower level start_server and keep track of it.
    yield srv
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

@pytest.mark.asyncio
async def test_full_lifecycle():
    received_messages = []

    async def handler(conn, payload):
        received_messages.append(payload)
        await conn.send(f"Echo: {payload}")

    srv = WebSocketServer(handler=handler)
    # Start server on a random port
    server = await asyncio.start_server(srv._handle_connection, "127.0.0.1", 0)
    addr = server.sockets[0].getsockname()
    host, port = addr[0], addr[1]

    server_task = asyncio.create_task(server.serve_forever())

    # Client side
    reader, writer = await asyncio.open_connection(host, port)

    # 1. Handshake
    handshake = (
        f"GET / HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
        f"Sec-WebSocket-Version: 13\r\n"
        f"\r\n"
    ).encode()
    writer.write(handshake)
    await writer.drain()

    response = await reader.read(4096)
    assert b"101 Switching Protocols" in response
    assert b"Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=" in response

    # 2. Send Message
    msg = "Hello server"
    # Client MUST mask frames
    frame_bytes = encode_frame(Opcode.TEXT, msg, mask=True)
    writer.write(frame_bytes)
    await writer.drain()

    # 3. Receive Echo
    echo_data = await reader.read(4096)
    echo_frame, _ = decode_frame(echo_data, from_client=False)
    assert echo_frame.payload == f"Echo: {msg}"
    assert received_messages == [msg]

    # 4. Ping/Pong
    ping_frame = encode_frame(Opcode.PING, b"ping data", mask=True)
    writer.write(ping_frame)
    await writer.drain()

    pong_data = await reader.read(4096)
    pong_frame, _ = decode_frame(pong_data, from_client=False)
    assert pong_frame.opcode == Opcode.PONG
    assert pong_frame.payload == b"ping data"

    # 5. Close
    close_frame = encode_frame(Opcode.CLOSE, b"", mask=True)
    writer.write(close_frame)
    await writer.drain()

    # Server should send close back and close connection
    close_resp = await reader.read(4096)
    assert close_resp # Should get something
    close_resp_frame, _ = decode_frame(close_resp, from_client=False)
    assert close_resp_frame.opcode == Opcode.CLOSE

    # Wait for EOF
    data = await reader.read(1024)
    assert data == b""
    assert reader.at_eof()

    writer.close()
    await writer.wait_closed()
    server.close()
    await server.wait_closed()
    server_task.cancel()

@pytest.mark.asyncio
async def test_server_binary_and_on_connect():
    on_connect_called = False
    on_disconnect_called = False

    async def on_connect(conn):
        nonlocal on_connect_called
        on_connect_called = True

    async def on_disconnect(conn):
        nonlocal on_disconnect_called
        on_disconnect_called = True

    async def handler(conn, payload):
        if isinstance(payload, bytes):
            await conn.send(payload)

    srv = WebSocketServer(handler=handler, on_connect=on_connect, on_disconnect=on_disconnect)
    server = await asyncio.start_server(srv._handle_connection, "127.0.0.1", 0)
    addr = server.sockets[0].getsockname()
    host, port = addr[0], addr[1]
    server_task = asyncio.create_task(server.serve_forever())

    reader, writer = await asyncio.open_connection(host, port)

    # Handshake
    handshake = (
        f"GET / HTTP/1.1\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
        f"Sec-WebSocket-Version: 13\r\n"
        f"\r\n"
    ).encode()
    writer.write(handshake)
    await writer.drain()
    await reader.read(4096)

    assert on_connect_called is True

    # Binary message
    msg = b"\xde\xad\xbe\xef"
    frame_bytes = encode_frame(Opcode.BINARY, msg, mask=True)
    writer.write(frame_bytes)
    await writer.drain()

    echo_data = await reader.read(4096)
    echo_frame, _ = decode_frame(echo_data, from_client=False)
    assert echo_frame.opcode == Opcode.BINARY
    assert echo_frame.payload == msg

    # Disconnect
    writer.close()
    await writer.wait_closed()

    # Wait a bit for server to process disconnect
    await asyncio.sleep(0.1)
    assert on_disconnect_called is True

    server.close()
    await server.wait_closed()
    server_task.cancel()

@pytest.mark.asyncio
async def test_server_large_frame():
    srv = WebSocketServer(handler=echo_handler)
    server = await asyncio.start_server(srv._handle_connection, "127.0.0.1", 0)
    addr = server.sockets[0].getsockname()
    host, port = addr[0], addr[1]
    server_task = asyncio.create_task(server.serve_forever())

    reader, writer = await asyncio.open_connection(host, port)

    # Handshake
    handshake = (
        f"GET / HTTP/1.1\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
        f"Sec-WebSocket-Version: 13\r\n"
        f"\r\n"
    ).encode()
    writer.write(handshake)
    await writer.drain()
    await reader.read(4096)

    # Large message (> 125, but < 65536)
    msg = "A" * 500
    frame_bytes = encode_frame(Opcode.TEXT, msg, mask=True)
    writer.write(frame_bytes)
    await writer.drain()

    echo_data = await reader.read(1024)
    echo_frame, _ = decode_frame(echo_data, from_client=False)
    assert echo_frame.payload == msg

    writer.close()
    await writer.wait_closed()
    server.close()
    await server.wait_closed()
    server_task.cancel()

@pytest.mark.asyncio
async def test_server_partial_frames():
    srv = WebSocketServer(handler=echo_handler)
    server = await asyncio.start_server(srv._handle_connection, "127.0.0.1", 0)
    addr = server.sockets[0].getsockname()
    host, port = addr[0], addr[1]
    server_task = asyncio.create_task(server.serve_forever())

    reader, writer = await asyncio.open_connection(host, port)

    # Handshake
    handshake = (
        f"GET / HTTP/1.1\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
        f"Sec-WebSocket-Version: 13\r\n"
        f"\r\n"
    ).encode()
    writer.write(handshake)
    await writer.drain()
    await reader.read(4096)

    # Send frame in chunks
    msg = "Chunked message"
    frame_bytes = encode_frame(Opcode.TEXT, msg, mask=True)

    writer.write(frame_bytes[:2])
    await writer.drain()
    await asyncio.sleep(0.1)

    writer.write(frame_bytes[2:])
    await writer.drain()

    echo_data = await reader.read(1024)
    echo_frame, _ = decode_frame(echo_data, from_client=False)
    assert echo_frame.payload == msg

    writer.close()
    await writer.wait_closed()
    server.close()
    await server.wait_closed()
    server_task.cancel()

@pytest.mark.asyncio
async def test_server_ping_pong():
    srv = WebSocketServer()
    server = await asyncio.start_server(srv._handle_connection, "127.0.0.1", 0)
    addr = server.sockets[0].getsockname()
    host, port = addr[0], addr[1]
    server_task = asyncio.create_task(server.serve_forever())

    reader, writer = await asyncio.open_connection(host, port)

    # Handshake
    handshake = (
        f"GET / HTTP/1.1\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
        f"Sec-WebSocket-Version: 13\r\n"
        f"\r\n"
    ).encode()
    writer.write(handshake)
    await writer.drain()
    await reader.read(4096)

    # 1. Send Ping
    ping_payload = b"test ping"
    writer.write(encode_frame(Opcode.PING, ping_payload, mask=True))
    await writer.drain()

    pong_data = await reader.read(1024)
    pong_frame, _ = decode_frame(pong_data, from_client=False)
    assert pong_frame.opcode == Opcode.PONG
    assert pong_frame.payload == ping_payload

    # 2. Server Sends Ping (using on_connect to trigger)
    # Actually let's just use the srv.connections to get the connection
    conn = list(srv.connections)[0]
    await conn.ping(b"server ping")

    ping_data = await reader.read(1024)
    ping_frame, _ = decode_frame(ping_data, from_client=False)
    assert ping_frame.opcode == Opcode.PING
    assert ping_frame.payload == b"server ping"

    # Client sends Pong
    writer.write(encode_frame(Opcode.PONG, b"server ping", mask=True))
    await writer.drain()
    # (Server just ignores PONG in our current implementation)

    writer.close()
    await writer.wait_closed()
    server.close()
    await server.wait_closed()
    server_task.cancel()

@pytest.mark.asyncio
async def test_server_handshake_invalid_upgrade():
    srv = WebSocketServer()
    server = await asyncio.start_server(srv._handle_connection, "127.0.0.1", 0)
    addr = server.sockets[0].getsockname()
    host, port = addr[0], addr[1]
    server_task = asyncio.create_task(server.serve_forever())

    reader, writer = await asyncio.open_connection(host, port)

    # Handshake with missing Upgrade
    handshake = (
        f"GET / HTTP/1.1\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: somekey\r\n"
        f"\r\n"
    ).encode()
    writer.write(handshake)
    await writer.drain()

    response = await reader.read(4096)
    assert b"400 Bad Request" in response

    writer.close()
    await writer.wait_closed()
    server.close()
    await server.wait_closed()
    server_task.cancel()

@pytest.mark.asyncio
async def test_server_invalid_frame_protocol_error():
    srv = WebSocketServer()
    server = await asyncio.start_server(srv._handle_connection, "127.0.0.1", 0)
    addr = server.sockets[0].getsockname()
    host, port = addr[0], addr[1]
    server_task = asyncio.create_task(server.serve_forever())

    reader, writer = await asyncio.open_connection(host, port)

    # Handshake
    handshake = (
        f"GET / HTTP/1.1\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
        f"Sec-WebSocket-Version: 13\r\n"
        f"\r\n"
    ).encode()
    writer.write(handshake)
    await writer.drain()
    await reader.read(4096)

    # Send invalid frame (opcode 3 is reserved)
    writer.write(bytes([0x83, 0x00]))
    await writer.drain()

    # Server should send close frame with protocol error (1002)
    close_data = await reader.read(1024)
    close_frame, _ = decode_frame(close_data, from_client=False)
    assert close_frame.opcode == Opcode.CLOSE
    # Payload should start with 1002
    assert int.from_bytes(close_frame.payload[:2], "big") == 1002

    writer.close()
    await writer.wait_closed()
    server.close()
    await server.wait_closed()
    server_task.cancel()

@pytest.mark.asyncio
async def test_server_connection_reset():
    srv = WebSocketServer()
    server = await asyncio.start_server(srv._handle_connection, "127.0.0.1", 0)
    addr = server.sockets[0].getsockname()
    host, port = addr[0], addr[1]
    server_task = asyncio.create_task(server.serve_forever())

    reader, writer = await asyncio.open_connection(host, port)

    # Handshake
    handshake = (
        f"GET / HTTP/1.1\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
        f"Sec-WebSocket-Version: 13\r\n"
        f"\r\n"
    ).encode()
    writer.write(handshake)
    await writer.drain()
    await reader.read(4096)

    # Force close connection without close frame
    writer.close()
    await writer.wait_closed()

    # Wait for server to finish
    await asyncio.sleep(0.1)

    server.close()
    await server.wait_closed()
    server_task.cancel()

@pytest.mark.asyncio
async def test_server_sync_handlers():
    # Test that it works even if handlers are synchronous
    on_connect_called = False

    def on_connect(conn):
        nonlocal on_connect_called
        on_connect_called = True

    def handler(conn, payload):
        # We can't await in sync handler, but we can't easily call async from sync either
        # This test is just to see if it doesn't crash
        pass

    srv = WebSocketServer(handler=handler, on_connect=on_connect)
    server = await asyncio.start_server(srv._handle_connection, "127.0.0.1", 0)
    addr = server.sockets[0].getsockname()
    host, port = addr[0], addr[1]
    server_task = asyncio.create_task(server.serve_forever())

    reader, writer = await asyncio.open_connection(host, port)

    # Handshake
    handshake = (
        f"GET / HTTP/1.1\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
        f"Sec-WebSocket-Version: 13\r\n"
        f"\r\n"
    ).encode()
    writer.write(handshake)
    await writer.drain()
    await reader.read(4096)

    assert on_connect_called is True

    # Message
    writer.write(encode_frame(Opcode.TEXT, "test", mask=True))
    await writer.drain()

    writer.close()
    await writer.wait_closed()
    server.close()
    await server.wait_closed()
    server_task.cancel()

@pytest.mark.asyncio
async def test_server_fragmentation():
    received = []
    async def handler(conn, payload):
        received.append(payload)

    srv = WebSocketServer(handler=handler)
    server = await asyncio.start_server(srv._handle_connection, "127.0.0.1", 0)
    addr = server.sockets[0].getsockname()
    host, port = addr[0], addr[1]
    server_task = asyncio.create_task(server.serve_forever())

    reader, writer = await asyncio.open_connection(host, port)

    # Handshake
    handshake = (
        f"GET / HTTP/1.1\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: somekey\r\n"
        f"Sec-WebSocket-Version: 13\r\n"
        f"\r\n"
    ).encode()
    writer.write(handshake)
    await writer.drain()
    await reader.read(4096)

    # Fragmented message
    # 1. Text fragment (FIN=0, TEXT)
    writer.write(encode_frame(Opcode.TEXT, "Hello ", fin=False, mask=True))
    # 2. Continuation fragment (FIN=0, CONT)
    writer.write(encode_frame(Opcode.CONTINUATION, "beautiful ", fin=False, mask=True))
    # 3. Last continuation fragment (FIN=1, CONT)
    writer.write(encode_frame(Opcode.CONTINUATION, "world", fin=True, mask=True))
    await writer.drain()

    # Wait a bit for server to process
    await asyncio.sleep(0.1)
    assert received == ["Hello beautiful world"]

    writer.close()
    await writer.wait_closed()
    server.close()
    await server.wait_closed()
    server_task.cancel()

@pytest.mark.asyncio
async def test_handshake_failure():
    srv = WebSocketServer()
    server = await asyncio.start_server(srv._handle_connection, "127.0.0.1", 0)
    addr = server.sockets[0].getsockname()
    host, port = addr[0], addr[1]
    server_task = asyncio.create_task(server.serve_forever())

    reader, writer = await asyncio.open_connection(host, port)
    writer.write(b"GET / HTTP/1.1\r\n\r\n") # Missing headers
    await writer.drain()

    response = await reader.read(4096)
    assert b"400 Bad Request" in response
    # Wait for EOF
    data = await reader.read(1024)
    assert data == b""
    assert reader.at_eof()

    writer.close()
    await writer.wait_closed()
    server.close()
    await server.wait_closed()
    server_task.cancel()
