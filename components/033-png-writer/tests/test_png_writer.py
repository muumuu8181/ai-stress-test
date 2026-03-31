import pytest
import struct
import zlib
from src.png_writer import (
    create_chunk,
    create_ihdr,
    create_idat,
    create_iend,
    generate_png,
)


def test_create_chunk():
    chunk_type = b"TEST"
    data = b"Some test data"
    chunk = create_chunk(chunk_type, data)

    # Check length
    length = struct.unpack(">I", chunk[:4])[0]
    assert length == len(data)

    # Check chunk type
    assert chunk[4:8] == chunk_type

    # Check data
    assert chunk[8 : 8 + len(data)] == data

    # Check CRC
    crc = struct.unpack(">I", chunk[8 + len(data) :])[0]
    expected_crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
    assert crc == expected_crc


def test_create_chunk_invalid_type():
    with pytest.raises(ValueError, match="chunk_type must be 4 bytes long"):
        create_chunk(b"ABC", b"data")


def test_create_ihdr():
    width, height = 10, 20
    ihdr = create_ihdr(width, height)

    assert ihdr[4:8] == b"IHDR"
    data = ihdr[8:21]  # 13 bytes of IHDR data
    w, h, depth, color, comp, filt, interl = struct.unpack(">IIBBBBB", data)
    assert w == width
    assert h == height
    assert depth == 8
    assert color == 2
    assert comp == 0
    assert filt == 0
    assert interl == 0


def test_create_idat():
    data = b"compressed-data"
    idat = create_idat(data)
    assert idat[4:8] == b"IDAT"
    assert idat[8 : 8 + len(data)] == data


def test_create_iend():
    iend = create_iend()
    assert iend[4:8] == b"IEND"
    assert iend[8:12] == b"\xaeB`\x82"  # Fixed CRC for empty IEND


def test_generate_png_basic():
    width, height = 2, 2
    # 2x2 white image
    rgb_data = bytes([255, 255, 255] * 4)
    png_bytes = generate_png(width, height, rgb_data)

    # Check signature
    assert png_bytes.startswith(b"\x89PNG\r\n\x1a\n")
    # Check if it contains required chunks
    assert b"IHDR" in png_bytes
    assert b"IDAT" in png_bytes
    assert b"IEND" in png_bytes


def test_generate_png_invalid_data_length():
    with pytest.raises(ValueError, match="rgb_data length"):
        generate_png(2, 2, b"\x00" * 10)  # Should be 12 bytes
