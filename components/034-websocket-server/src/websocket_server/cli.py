import argparse
import asyncio
import logging
from typing import Union
from .server import WebSocketServer, WebSocketConnection

logger = logging.getLogger(__name__)

async def echo_handler(conn: WebSocketConnection, payload: Union[str, bytes]):
    """A simple echo handler that sends back the received payload."""
    logger.info(f"Received message: {payload}")
    await conn.send(payload)

async def main():
    parser = argparse.ArgumentParser(description="WebSocket Server CLI")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind (default: 8765)")

    args = parser.parse_args()

    server = WebSocketServer(handler=echo_handler)

    logger.info(f"Starting server on {args.host}:{args.port}")
    try:
        await server.start(args.host, args.port)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
