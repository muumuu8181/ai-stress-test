import pytest
from qr_encoder.encoding import encode_numeric, encode_alphanumeric, encode_byte, get_version_and_data_bits, bits_to_codewords
from qr_encoder.constants import Mode, ErrorCorrectionLevel

def test_encode_numeric():
    assert encode_numeric("123") == "0001111011" # 123 (10 bits)
    # 45(7) should be 0101101
    assert encode_numeric("12345") == "00011110110101101" # 123(10), 45(7)
    # 7(4) should be 0111
    assert encode_numeric("1234567") == "000111101101110010000111" # 123(10), 456(10), 7(4)

def test_encode_alphanumeric():
    # AC: 10*45 + 12 = 450+12 = 462 (11 bits)
    assert encode_alphanumeric("AC") == f"{462:011b}"
    # AC1: AC(11), 1(6)
    assert encode_alphanumeric("AC1") == f"{462:011b}{1:06b}"

def test_encode_byte():
    assert encode_byte("A") == "01000001"
    assert encode_byte("HELLO") == "".join(f"{ord(c):08b}" for c in "HELLO")

def test_get_version_and_data_bits():
    # HELLO can be alphanumeric!
    version, mode, bits = get_version_and_data_bits("HELLO!", ErrorCorrectionLevel.M)
    assert version == 1
    assert mode == Mode.BYTE
    # HELLO! in byte mode: mode(0100), count(00000110), data(8 bits each * 6)
    # Total = 4 + 8 + 48 = 60 bits.
    # Version 1 Level M total data capacity = 16 * 8 = 128 bits.
    assert len(bits) == 128
    assert bits.startswith("010000000110") # Mode 4, count 6

def test_bits_to_codewords():
    bits = "0100000001010100"
    cw = bits_to_codewords(bits)
    assert cw == [64, 84]

def test_data_too_large():
    with pytest.raises(ValueError):
        get_version_and_data_bits("A" * 2000, ErrorCorrectionLevel.H)
