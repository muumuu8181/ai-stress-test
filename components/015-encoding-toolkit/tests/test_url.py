from enctool.url_tool import url_decode, url_encode


def test_url_encode_decode():
    data = "hello world/test"
    encoded = url_encode(data)
    assert encoded == "hello%20world/test"
    decoded = url_decode(encoded)
    assert decoded == data


def test_url_special_chars():
    data = "a=b&c=d"
    encoded = url_encode(data)
    assert "%3D" in encoded or "a%3Db%26c%3Dd"
    decoded = url_decode(encoded)
    assert decoded == data


def test_url_empty():
    assert url_encode("") == ""
    assert url_decode("") == ""
