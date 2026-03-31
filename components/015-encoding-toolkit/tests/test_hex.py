import pytest

from enctool.hex_tool import hex_decode, hex_encode


def test_hex_encode_decode():
    data = b"hello"
    encoded = hex_encode(data)
    assert encoded == "68656c6c6f"
    decoded = hex_decode(encoded)
    assert decoded == data


def test_hex_empty():
    assert hex_encode(b"") == ""
    assert hex_decode("") == b""


def test_hex_invalid():
    with pytest.raises(ValueError, match="Invalid hex input"):
        hex_decode("not-a-hex")
