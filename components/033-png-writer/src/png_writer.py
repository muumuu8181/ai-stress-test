import struct
import zlib
from typing import List


def create_chunk(chunk_type: bytes, data: bytes) -> bytes:
    """
    Creates a PNG chunk.

    A PNG chunk consists of:
    - Length (4 bytes, big-endian)
    - Chunk Type (4 bytes)
    - Chunk Data (Length bytes)
    - CRC (4 bytes, big-endian) - calculated over Chunk Type and Chunk Data.

    Args:
        chunk_type: 4-byte bytes object representing the chunk type (e.g., b'IHDR').
        data: The data to be contained in the chunk.

    Returns:
        The complete PNG chunk as bytes.
    """
    if len(chunk_type) != 4:
        raise ValueError("chunk_type must be 4 bytes long")

    length = struct.pack(">I", len(data))
    crc = struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
    return length + chunk_type + data + crc


def create_ihdr(
    width: int,
    height: int,
    bit_depth: int = 8,
    color_type: int = 2,
    compression: int = 0,
    filter_method: int = 0,
    interlace: int = 0,
) -> bytes:
    """
    Creates an IHDR (Image Header) chunk.

    Args:
        width: Image width in pixels.
        height: Image height in pixels.
        bit_depth: Bit depth (usually 8).
        color_type: Color type (2 for RGB).
        compression: Compression method (0 for DEFLATE).
        filter_method: Filter method (0 for adaptive filtering).
        interlace: Interlace method (0 for no interlace).

    Returns:
        The IHDR chunk as bytes.
    """
    data = struct.pack(
        ">IIBBBBB",
        width,
        height,
        bit_depth,
        color_type,
        compression,
        filter_method,
        interlace,
    )
    return create_chunk(b"IHDR", data)


def create_idat(pixel_data: bytes) -> bytes:
    """
    Creates an IDAT (Image Data) chunk.

    Args:
        pixel_data: The compressed image data.

    Returns:
        The IDAT chunk as bytes.
    """
    return create_chunk(b"IDAT", pixel_data)


def create_iend() -> bytes:
    """
    Creates an IEND (Image End) chunk.

    Returns:
        The IEND chunk as bytes.
    """
    return create_chunk(b"IEND", b"")


def generate_png(width: int, height: int, rgb_data: bytes) -> bytes:
    """
    Generates a complete PNG image byte stream.

    Args:
        width: Image width.
        height: Image height.
        rgb_data: Raw RGB pixel data. Must have length width * height * 3.

    Returns:
        The complete PNG byte stream.
    """
    if len(rgb_data) != width * height * 3:
        raise ValueError(
            f"rgb_data length {len(rgb_data)} does not match width {width} * height {height} * 3"
        )

    # PNG signature
    signature = b"\x89PNG\r\n\x1a\n"

    # IHDR chunk
    ihdr = create_ihdr(width, height)

    # IDAT chunk
    # Each scanline must be preceded by a filter byte (0 for None)
    scanlines = []
    for y in range(height):
        scanline = rgb_data[y * width * 3 : (y + 1) * width * 3]
        scanlines.append(b"\x00" + scanline)

    data_to_compress = b"".join(scanlines)
    compressed_data = zlib.compress(data_to_compress)
    idat = create_idat(compressed_data)

    # IEND chunk
    iend = create_iend()

    return signature + ihdr + idat + iend
