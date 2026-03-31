import io
import pytest
from dnsclient.protocol import decode_dns_name


def test_decode_dns_name_pointer_cycle():
    # Pointer at offset 2 points to offset 2 (self)
    data = b"\x00\x00\xc0\x02"
    reader = io.BytesIO(data)
    reader.seek(2)
    with pytest.raises(ValueError, match="compression pointer cycle"):
        decode_dns_name(reader, data)


def test_decode_dns_name_long_cycle():
    # offset 0 points to offset 2
    # offset 2 points to offset 0
    data = b"\xc0\x02\xc0\x00"
    reader = io.BytesIO(data)
    with pytest.raises(ValueError, match="compression pointer cycle"):
        decode_dns_name(reader, data)
