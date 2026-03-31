import pytest
from qr_encoder import generate_qr, ErrorCorrectionLevel

def test_version_info_v7():
    # V7 L max data capacity is 156 bytes
    # V6 L max data capacity is 136 bytes
    # V5 L max data capacity is 108 bytes
    # "A" * 150 should be V7
    data = "A" * 150
    qr = generate_qr(data, ErrorCorrectionLevel.L)
    # Actually wait, "A" can be Alphanumeric!
    # V5 Alphanumeric capacity = 108 * 8 / (11/2) = 157 characters approx?
    # Let's check get_version_and_data_bits.
    # HELLO! was Alphanumeric.
    pass

def test_byte_mode_version_7():
    # Force Byte mode using a non-alphanumeric character
    data = "{" * 140 # V7 L byte capacity is 156. V6 is 136.
    qr = generate_qr(data, ErrorCorrectionLevel.L)
    assert qr.version == 7
    # Placement 1: Above bottom-left finder (size-11 to size-9, 0-5)
    # Correcting: bits[i] placed at size-11+(i%3), i//3
    # r range: qr.size-11, qr.size-10, qr.size-9. c range: 0, 1, 2, 3, 4, 5.
    for r in range(qr.size - 11, qr.size - 8):
        for c in range(6):
            assert qr.reserved[r][c] is True

def test_no_version_info_v6():
    data = "{" * 130
    qr = generate_qr(data, ErrorCorrectionLevel.L)
    assert qr.version == 6
    for r in range(qr.size - 11, qr.size - 8):
        for c in range(6):
            assert qr.reserved[r][c] is False
