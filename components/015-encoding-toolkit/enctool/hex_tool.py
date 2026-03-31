import binascii


def hex_encode(data: bytes) -> str:
    """Encode bytes to hex string.

    Args:
        data: The bytes to encode.

    Returns:
        The hex-encoded string.

    """
    return data.hex()


def hex_decode(data: str) -> bytes:
    """Decode hex string to bytes.

    Args:
        data: The hex-encoded string to decode.

    Returns:
        The decoded bytes.

    Raises:
        ValueError: If the input is not a valid hex string.

    """
    try:
        return bytes.fromhex(data)
    except (ValueError, binascii.Error) as e:
        raise ValueError(f"Invalid hex input: {e}")
