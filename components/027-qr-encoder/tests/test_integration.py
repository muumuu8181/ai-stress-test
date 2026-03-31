import pytest
from qr_encoder import generate_qr, to_ascii, to_pbm, ErrorCorrectionLevel

def test_integration_hello():
    qr = generate_qr("HELLO!")
    assert qr.size == 21
    ascii_out = to_ascii(qr)
    assert len(ascii_out.splitlines()) == 29

def test_different_ec_levels():
    for ec in ErrorCorrectionLevel:
        qr = generate_qr("HELLO!", ec)
        assert qr.size == 21

def test_numeric_mode():
    qr = generate_qr("123456789012345")
    assert qr.size == 21

def test_alphanumeric_mode():
    qr = generate_qr("HELLO 123 WORLD")
    assert qr.size == 21

def test_large_data_version_transition():
    # V1 Level L: 19 bytes
    # V2 Level L: 34 bytes
    data = "A" * 30
    qr = generate_qr(data, ErrorCorrectionLevel.L)
    assert qr.size == 25 # V2 size: (2-1)*4 + 21 = 25

def test_empty_input():
    qr = generate_qr("")
    assert qr.size == 21

def test_byte_mode_utf8():
    qr = generate_qr("こんにちは")
    # Each char is 3 bytes in UTF-8 -> 15 bytes.
    # Version 1 Level H: 9 bytes.
    # Version 2 Level H: 16 bytes.
    qr_h = generate_qr("こんにちは", ErrorCorrectionLevel.H)
    # The size seems to be 29 for some reason? V3?
    # (3-1)*4 + 21 = 29.
    # Why V3?
    # HELLO! in byte mode: mode(0100), count(00000110), data(8 bits each * 15)
    # Total = 4 + 8 + 120 = 132 bits.
    # V2 Level H capacity = 16 * 8 = 128 bits.
    # 132 > 128, so it needs V3.
    assert qr_h.size == 29
