import pytest

from enctool.base64_tool import base64_decode, base64_encode


def test_base64_encode_decode():
    data = b"hello"
    encoded = base64_encode(data)
    assert encoded == "aGVsbG8="
    decoded = base64_decode(encoded)
    assert decoded == data


def test_base64_url_safe():
    data = b"\xff\xfe\xfd"
    # Standard base64: //79
    # URL-safe base64: __79
    encoded = base64_encode(data, url_safe=True)
    assert "-" in encoded or "_" in encoded or encoded == "P_79"
    decoded = base64_decode(encoded, url_safe=True)
    assert decoded == data


def test_base64_empty():
    assert base64_encode(b"") == ""
    assert base64_decode("") == b""


def test_base64_invalid():
    with pytest.raises(ValueError, match="Invalid Base64 input"):
        base64_decode("invalid-base64!")
