import struct
from enum import IntEnum
from typing import Optional, Tuple, Union

class Opcode(IntEnum):
    """WebSocket opcodes as defined in RFC 6455."""
    CONTINUATION = 0x0
    TEXT = 0x1
    BINARY = 0x2
    CLOSE = 0x8
    PING = 0x9
    PONG = 0xA

class FrameError(Exception):
    """Exception raised for errors during frame parsing or generation."""
    pass

class IncompleteFrameError(FrameError):
    """Exception raised when a frame is incomplete and more data is needed."""
    pass

class Frame:
    """Represents a WebSocket frame."""
    def __init__(
        self,
        opcode: Opcode,
        payload: Union[str, bytes],
        fin: bool = True,
        mask: bool = False,
    ):
        self.opcode = opcode
        self.payload = payload
        self.fin = fin
        self.mask = mask

    def __repr__(self) -> str:
        return f"Frame(opcode={self.opcode!r}, payload_len={len(self.payload)}, fin={self.fin}, mask={self.mask})"

def decode_frame(data: bytes, from_client: bool = True) -> Tuple[Frame, int]:
    """
    Decodes a WebSocket frame from raw bytes.

    Args:
        data: The raw bytes received.
        from_client: Whether the frame is from a client (requires masking).

    Returns:
        A tuple containing the Frame object and the number of bytes consumed.

    Raises:
        FrameError: If the frame is invalid.
        IncompleteFrameError: If the frame is incomplete and more data is needed.
    """
    if len(data) < 2:
        raise IncompleteFrameError("Frame too short")

    first_byte, second_byte = struct.unpack("!BB", data[:2])
    fin = (first_byte & 0x80) != 0
    rsv = (first_byte & 0x70) >> 4
    if rsv != 0:
        raise FrameError("Reserved bits (RSV1, RSV2, RSV3) must be zero")

    opcode_value = first_byte & 0x0F
    try:
        opcode = Opcode(opcode_value)
    except ValueError:
        raise FrameError(f"Unknown opcode: {opcode_value}")

    # Control frame validation
    if opcode >= 0x8:
        if not fin:
            raise FrameError("Control frames must not be fragmented")
        if (second_byte & 0x7F) > 125:
            raise FrameError("Control frames must have payload length <= 125")

    mask_bit = (second_byte & 0x80) != 0
    if from_client and not mask_bit:
        # RFC 6455 Section 5.1: The server MUST close the connection
        # if it receives an unmasked frame.
        raise FrameError("Client frames must be masked")

    payload_len = second_byte & 0x7F

    offset = 2
    if payload_len == 126:
        if len(data) < offset + 2:
            raise IncompleteFrameError("Incomplete extended payload length (2 bytes)")
        payload_len = struct.unpack("!H", data[offset : offset + 2])[0]
        offset += 2
    elif payload_len == 127:
        if len(data) < offset + 8:
            raise IncompleteFrameError("Incomplete extended payload length (8 bytes)")
        payload_len = struct.unpack("!Q", data[offset : offset + 8])[0]
        offset += 8

    masking_key = None
    if mask_bit:
        if len(data) < offset + 4:
            raise IncompleteFrameError("Incomplete masking key")
        masking_key = data[offset : offset + 4]
        offset += 4

    if len(data) < offset + payload_len:
        raise IncompleteFrameError("Incomplete payload")

    payload = data[offset : offset + payload_len]
    offset += payload_len

    if masking_key:
        payload = bytes(b ^ masking_key[i % 4] for i, b in enumerate(payload))

    if opcode == Opcode.TEXT and fin:
        try:
            payload = payload.decode("utf-8")
        except UnicodeDecodeError:
            raise FrameError("Invalid UTF-8 in text frame")

    return Frame(opcode, payload, fin, mask_bit), offset

def encode_frame(
    opcode: Opcode,
    payload: Union[str, bytes],
    fin: bool = True,
    mask: bool = False,
) -> bytes:
    """
    Encodes a WebSocket frame into raw bytes.

    Args:
        opcode: The Opcode for the frame.
        payload: The payload to include (str or bytes).
        fin: Whether this is the final frame.
        mask: Whether to mask the payload (usually False for server-to-client).

    Returns:
        The raw bytes of the encoded frame.
    """
    if isinstance(payload, str):
        payload = payload.encode("utf-8")

    first_byte = (0x80 if fin else 0x00) | int(opcode)
    second_byte = 0x80 if mask else 0x00
    payload_len = len(payload)

    header = bytearray([first_byte])

    if payload_len <= 125:
        header.append(second_byte | payload_len)
    elif payload_len <= 65535:
        header.append(second_byte | 126)
        header.extend(struct.pack("!H", payload_len))
    else:
        header.append(second_byte | 127)
        header.extend(struct.pack("!Q", payload_len))

    if mask:
        import os
        masking_key = os.urandom(4)
        header.extend(masking_key)
        masked_payload = bytes(b ^ masking_key[i % 4] for i, b in enumerate(payload))
        return bytes(header) + masked_payload

    return bytes(header) + payload
