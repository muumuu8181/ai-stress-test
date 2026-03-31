import base64


def base64_encode(data: bytes, url_safe: bool = False) -> str:
    """Encode bytes to Base64 string.

    Args:
        data: The bytes to encode.
        url_safe: Whether to use URL-safe Base64 encoding.

    Returns:
        The Base64 encoded string.

    """
    if url_safe:
        return base64.urlsafe_b64encode(data).decode("ascii")
    return base64.b64encode(data).decode("ascii")


def base64_decode(data: str, url_safe: bool = False) -> bytes:
    """Decode Base64 string to bytes.

    Args:
        data: The Base64 string to decode.
        url_safe: Whether to use URL-safe Base64 decoding.

    Returns:
        The decoded bytes.

    Raises:
        ValueError: If the input is not a valid Base64 string.

    """
    try:
        if url_safe:
            return base64.urlsafe_b64decode(data)
        return base64.b64decode(data)
    except Exception as e:
        raise ValueError(f"Invalid Base64 input: {e}")
