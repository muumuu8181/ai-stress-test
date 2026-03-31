from typing import Optional


def convert_encoding(data: bytes, from_enc: str, to_enc: str) -> bytes:
    """Convert bytes from one encoding to another.

    Args:
        data: The input bytes.
        from_enc: The source encoding.
        to_enc: The target encoding.

    Returns:
        The converted bytes.

    """
    return data.decode(from_enc).encode(to_enc)


def detect_encoding(data: bytes) -> Optional[str]:
    """Heuristically detect the text encoding of the given bytes.
    Checks for BOMs and then tries to decode with several common encodings.

    Args:
        data: The bytes to detect encoding for.

    Returns:
        The name of the detected encoding, or None if detection failed.

    """
    # Check for BOMs first
    boms = [
        (b"\xef\xbb\xbf", "utf-8-sig"),
        (b"\xff\xfe\x00\x00", "utf-32-le"),
        (b"\x00\x00\xfe\xff", "utf-32-be"),
        (b"\xff\xfe", "utf-16-le"),
        (b"\xfe\xff", "utf-16-be"),
    ]
    for bom, encoding in boms:
        if data.startswith(bom):
            return encoding

    # Try common encodings in order
    encodings = ["utf-8", "shift-jis", "euc-jp", "latin-1"]
    for enc in encodings:
        try:
            data.decode(enc)
            return enc
        except UnicodeDecodeError:
            continue

    return None
