from enctool.encoding_tool import convert_encoding, detect_encoding


def test_convert_encoding():
    data = "こんにちは"
    utf8_bytes = data.encode("utf-8")
    sjis_bytes = data.encode("shift-jis")

    converted = convert_encoding(utf8_bytes, "utf-8", "shift-jis")
    assert converted == sjis_bytes

    back = convert_encoding(sjis_bytes, "shift-jis", "utf-8")
    assert back == utf8_bytes


def test_detect_encoding_utf8():
    data = "こんにちは".encode("utf-8")
    assert detect_encoding(data) == "utf-8"


def test_detect_encoding_sjis():
    data = "こんにちは".encode("shift-jis")
    assert detect_encoding(data) == "shift-jis"


def test_detect_encoding_bom():
    data = b"\xef\xbb\xbfhello"
    assert detect_encoding(data) == "utf-8-sig"


def test_detect_encoding_unknown():
    # Random bytes that might not be valid in any of the tested encodings
    data = b"\xff\xff\xff\xff"
    assert detect_encoding(data) in ["latin-1", None]
