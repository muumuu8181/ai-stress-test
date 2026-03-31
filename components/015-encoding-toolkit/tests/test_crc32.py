import zlib

from enctool.crc32_tool import calculate_crc32


def test_calculate_crc32():
    data = b"hello world"
    expected = f"{zlib.crc32(data) & 0xFFFFFFFF:08x}"
    assert calculate_crc32(data) == expected


def test_crc32_empty():
    data = b""
    expected = f"{zlib.crc32(data) & 0xFFFFFFFF:08x}"
    assert calculate_crc32(data) == expected


def test_crc32_large():
    data = b"\xff" * 1024
    expected = f"{zlib.crc32(data) & 0xFFFFFFFF:08x}"
    assert calculate_crc32(data) == expected
