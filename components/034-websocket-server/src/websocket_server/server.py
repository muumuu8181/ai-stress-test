import asyncio
import logging
from typing import Callable, Optional, Set, Union

from .handshake import (
    HandshakeError,
    build_handshake_response,
    generate_accept_key,
    parse_http_headers,
    validate_handshake,
)
from .frame import Frame, FrameError, IncompleteFrameError, Opcode, decode_frame, encode_frame

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketConnection:
    """Represents a single WebSocket connection."""
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self.closed = False

    async def send(self, payload: Union[str, bytes]):
        """Sends a message to the client."""
        opcode = Opcode.TEXT if isinstance(payload, str) else Opcode.BINARY
        frame_bytes = encode_frame(opcode, payload)
        self.writer.write(frame_bytes)
        await self.writer.drain()

    async def ping(self, payload: bytes = b""):
        """Sends a ping frame to the client."""
        frame_bytes = encode_frame(Opcode.PING, payload)
        self.writer.write(frame_bytes)
        await self.writer.drain()

    async def pong(self, payload: bytes = b""):
        """Sends a pong frame to the client."""
        frame_bytes = encode_frame(Opcode.PONG, payload)
        self.writer.write(frame_bytes)
        await self.writer.drain()

    async def close(self, code: int = 1000, reason: str = ""):
        """Sends a close frame and closes the connection."""
        if self.closed:
            return
        payload = code.to_bytes(2, "big") + reason.encode("utf-8")
        frame_bytes = encode_frame(Opcode.CLOSE, payload)
        self.writer.write(frame_bytes)
        await self.writer.drain()
        self.writer.close()
        await self.writer.wait_closed()
        self.closed = True

class WebSocketServer:
    """A simple WebSocket server implementation."""
    def __init__(
        self,
        handler: Callable[[WebSocketConnection, Union[str, bytes]], asyncio.Future] = None,
        on_connect: Callable[[WebSocketConnection], asyncio.Future] = None,
        on_disconnect: Callable[[WebSocketConnection], asyncio.Future] = None,
    ):
        self.handler = handler
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.connections: Set[WebSocketConnection] = set()
        self._frag_buffer = bytearray()
        self._frag_opcode = None

    async def _handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Internal handler for new TCP connections."""
        peer = writer.get_extra_info("peername")
        logger.info(f"New connection from {peer}")

        try:
            # 1. Perform Handshake
            request_data = b""
            while True:
                chunk = await reader.read(4096)
                if not chunk:
                    break
                request_data += chunk
                if b"\r\n\r\n" in request_data:
                    break

            if not request_data:
                writer.close()
                return

            parts = request_data.split(b"\r\n\r\n", 1)
            handshake_bytes = parts[0] + b"\r\n\r\n"
            buffer = parts[1] if len(parts) > 1 else b""

            request_line, headers = parse_http_headers(handshake_bytes)
            sec_key = validate_handshake(request_line, headers)
            accept_key = generate_accept_key(sec_key)
            response = build_handshake_response(accept_key)

            writer.write(response)
            await writer.drain()

            conn = WebSocketConnection(reader, writer)
            self.connections.add(conn)

            if self.on_connect:
                res = self.on_connect(conn)
                if asyncio.iscoroutine(res):
                    await res

            # 2. Frame processing loop
            while not conn.closed:
                try:
                    # Process all complete frames currently in the buffer
                    while buffer:
                        try:
                            frame, consumed = decode_frame(buffer)
                            buffer = buffer[consumed:]
                            await self._process_frame(conn, frame)
                        except IncompleteFrameError:
                            # Wait for more data
                            break
                        except FrameError as e:
                            logger.error(f"Frame error: {e}")
                            await conn.close(code=1002, reason="Protocol error")
                            break

                    if conn.closed:
                        break

                    # Wait for new data from the network
                    chunk = await reader.read(4096)
                    if not chunk:
                        break
                    buffer += chunk

                except ConnectionResetError:
                    break
                except Exception as e:
                    logger.exception(f"Error handling connection: {e}")
                    break

        except HandshakeError as e:
            logger.error(f"Handshake error: {e}")
            writer.write(b"HTTP/1.1 400 Bad Request\r\n\r\n")
            await writer.drain()
            writer.close()
        finally:
            if 'conn' in locals():
                self.connections.discard(conn)
                if self.on_disconnect:
                    res = self.on_disconnect(conn)
                    if asyncio.iscoroutine(res):
                        await res
                if not conn.closed:
                    writer.close()
                    await writer.wait_closed()
            else:
                writer.close()
            logger.info(f"Connection closed for {peer}")

    async def _process_frame(self, conn: WebSocketConnection, frame: Frame):
        """Processes a single decoded WebSocket frame."""
        if frame.opcode == Opcode.CLOSE:
            await conn.close()
        elif frame.opcode == Opcode.PING:
            await conn.pong(frame.payload)
        elif frame.opcode == Opcode.PONG:
            pass  # Received pong
        elif frame.opcode in (Opcode.TEXT, Opcode.BINARY):
            if not frame.fin:
                self._frag_buffer.extend(frame.payload.encode("utf-8") if isinstance(frame.payload, str) else frame.payload)
                self._frag_opcode = frame.opcode
            else:
                if self.handler:
                    res = self.handler(conn, frame.payload)
                    if asyncio.iscoroutine(res):
                        await res
        elif frame.opcode == Opcode.CONTINUATION:
            if self._frag_opcode is None:
                raise FrameError("Received continuation frame without preceding fragment")

            self._frag_buffer.extend(frame.payload.encode("utf-8") if isinstance(frame.payload, str) else frame.payload)

            if frame.fin:
                full_payload = bytes(self._frag_buffer)
                if self._frag_opcode == Opcode.TEXT:
                    try:
                        full_payload = full_payload.decode("utf-8")
                    except UnicodeDecodeError:
                        raise FrameError("Invalid UTF-8 in fragmented text message")

                if self.handler:
                    res = self.handler(conn, full_payload)
                    if asyncio.iscoroutine(res):
                        await res

                self._frag_buffer.clear()
                self._frag_opcode = None

    async def start(self, host: str, port: int):
        """Starts the WebSocket server."""
        server = await asyncio.start_server(self._handle_connection, host, port)
        addr = server.sockets[0].getsockname()
        logger.info(f"Serving on {addr}")
        async with server:
            await server.serve_forever()
