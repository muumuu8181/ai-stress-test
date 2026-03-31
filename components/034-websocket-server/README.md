# WebSocket Server

An RFC 6455 compliant WebSocket server implementation in Python using `asyncio`.

## Features

- Complete WebSocket Handshake handling.
- Frame parsing and generation (supporting Text, Binary, Ping, Pong, and Close frames).
- Support for masked frames (required for client-to-server communication).
- Handles large payloads (16-bit and 64-bit lengths).
- Asyncio-based server for high concurrency.
- Simple API with connection and message handlers.
- CLI for quick startup.

## Requirements

- Python 3.7+

## Installation

No external dependencies are required for the core server. For testing and development:

```bash
pip install pytest pytest-asyncio pytest-cov
```

## Usage

### Simple Echo Server

```python
import asyncio
from websocket_server.server import WebSocketServer, WebSocketConnection

async def handle_message(conn: WebSocketConnection, payload: str):
    print(f"Received: {payload}")
    await conn.send(f"Echo: {payload}")

async def main():
    server = WebSocketServer(handler=handle_message)
    await server.start("127.0.0.1", 8765)

if __name__ == "__main__":
    asyncio.run(main())
```

### CLI

You can start a default echo server using the provided CLI:

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python3 -m websocket_server.cli --host 127.0.0.1 --port 8765
```

## API Reference

### `WebSocketServer`

- `__init__(handler=None, on_connect=None, on_disconnect=None)`
    - `handler(conn, payload)`: Called when a text or binary message is received.
    - `on_connect(conn)`: Called when a new WebSocket connection is established.
    - `on_disconnect(conn)`: Called when a connection is closed.
- `start(host, port)`: Coroutine that starts the TCP server and begins accepting connections.

### `WebSocketConnection`

- `send(payload)`: Sends a text (if payload is `str`) or binary (if payload is `bytes`) message.
- `ping(payload=b"")`: Sends a ping frame.
- `pong(payload=b"")`: Sends a pong frame.
- `close(code=1000, reason="")`: Sends a close frame and closes the connection.

## Testing

Run tests with `pytest`:

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
pytest tests/
```

To run with coverage:

```bash
pytest --cov=websocket_server tests/
```
