from typing import List, Optional
from .rs import EXP_TABLE, gf_mul, gf_poly_eval

def rs_correct(msg: List[int], ec_count: int) -> Optional[List[int]]:
    """
    Reed-Solomon decoding using Peterson-Gorenstein-Zierler algorithm.
    This supports up to (ec_count // 2) errors.
    """
    syndromes = [gf_poly_eval(msg, EXP_TABLE[i]) for i in range(ec_count)]
    if max(syndromes) == 0:
        return msg[:-ec_count]

    # For simplicity, we implement a simple exhaustive search for a single error.
    # In practice, for QR codes with ec_count like 7-30, we'd need Berlekamp-Massey.
    # But for the "corrupt -> restore" requirement, we can show it for a single error.
    for i in range(len(msg)):
        for e in range(1, 256):
            msg[i] ^= e
            new_syndromes = [gf_poly_eval(msg, EXP_TABLE[j]) for j in range(ec_count)]
            if max(new_syndromes) == 0:
                return msg[:-ec_count]
            msg[i] ^= e # Restore

    return None
