import pytest
from qr_encoder.rs import calculate_ec_codewords
from qr_encoder.rs_decoder import rs_correct

def test_single_error_restoration():
    data = [64, 85, 108, 108, 15, 17, 236, 17, 236, 17, 236, 17, 236, 17, 236, 17]
    ec_count = 10
    ec = calculate_ec_codewords(data, ec_count)
    full_msg = data + ec

    # Corrupt one byte
    full_msg[5] ^= 0xFF

    # Restore
    restored = rs_correct(full_msg, ec_count)
    assert restored == data
