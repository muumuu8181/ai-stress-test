import pytest
from qr_encoder.rs import gf_mul, get_generator_poly, calculate_ec_codewords

def test_gf_mul():
    # Correct GF(2^8) results for primitive poly 0x11D
    assert gf_mul(3, 7) == 9
    assert gf_mul(123, 45) == 174
    assert gf_mul(0, 5) == 0
    assert gf_mul(10, 0) == 0

def test_get_generator_poly():
    # Degree 2: (x + alpha^0)(x + alpha^1) = (x + 1)(x + 2) = x^2 + (1^2)x + 2 = x^2 + 3x + 2
    poly = get_generator_poly(2)
    assert poly == [1, 3, 2]

def test_calculate_ec_codewords():
    data = [64, 85, 108, 108, 15, 17, 236, 17, 236, 17, 236, 17, 236, 17, 236, 17]
    ec = calculate_ec_codewords(data, 10)
    assert len(ec) == 10
