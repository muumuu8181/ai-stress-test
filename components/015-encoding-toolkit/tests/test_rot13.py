from enctool.rot13_tool import rot13


def test_rot13():
    data = "hello world"
    encoded = rot13(data)
    assert encoded == "uryyb jbeyq"
    decoded = rot13(encoded)
    assert decoded == data


def test_rot13_empty():
    assert rot13("") == ""


def test_rot13_numbers():
    assert rot13("123") == "123"
