import urllib.parse


def url_encode(data: str) -> str:
    """URL-encode a string.

    Args:
        data: The string to encode.

    Returns:
        The URL-encoded string.

    """
    return urllib.parse.quote(data)


def url_decode(data: str) -> str:
    """URL-decode a string.

    Args:
        data: The URL-encoded string to decode.

    Returns:
        The decoded string.

    """
    return urllib.parse.unquote(data)
