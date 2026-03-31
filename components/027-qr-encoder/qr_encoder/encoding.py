import math
from typing import List, Tuple
from .constants import Mode, EC_CONFIG, get_char_count_indicator_bits, ALPHANUMERIC_CHARS, ErrorCorrectionLevel

def get_best_mode(data: str) -> Mode:
    """
    Selects the most efficient encoding mode for the given data.
    """
    # Strict ASCII digit check to avoid matching non-ASCII Unicode digits
    if all('0' <= c <= '9' for c in data):
        return Mode.NUMERIC
    if all(c in ALPHANUMERIC_CHARS for c in data):
        return Mode.ALPHANUMERIC
    return Mode.BYTE

def encode_numeric(data: str) -> str:
    """Encodes numeric data into bits."""
    bits = ""
    for i in range(0, len(data), 3):
        chunk = data[i:i+3]
        num = int(chunk)
        if len(chunk) == 3:
            bits += f"{num:010b}"
        elif len(chunk) == 2:
            bits += f"{num:07b}"
        else:
            bits += f"{num:04b}"
    return bits

def encode_alphanumeric(data: str) -> str:
    """Encodes alphanumeric data into bits."""
    bits = ""
    for i in range(0, len(data), 2):
        chunk = data[i:i+2]
        if len(chunk) == 2:
            val = ALPHANUMERIC_CHARS.find(chunk[0]) * 45 + ALPHANUMERIC_CHARS.find(chunk[1])
            bits += f"{val:011b}"
        else:
            val = ALPHANUMERIC_CHARS.find(chunk[0])
            bits += f"{val:06b}"
    return bits

def encode_byte(data: str) -> str:
    """Encodes byte data into bits."""
    bits = ""
    for b in data.encode("utf-8"):
        bits += f"{b:08b}"
    return bits

def get_version_and_data_bits(data: str, ec_level: ErrorCorrectionLevel) -> Tuple[int, Mode, str]:
    """
    Finds the smallest QR version that can hold the data and returns its version and encoded bits.
    """
    mode = get_best_mode(data)

    # Check if non-ASCII to determine if ECI is needed for Byte mode
    use_eci = False
    if mode == Mode.BYTE:
        try:
            data.encode("ascii")
        except UnicodeEncodeError:
            use_eci = True

    for version in range(1, 11):
        mode_bits = f"{mode.value:04b}"
        char_count_bits = get_char_count_indicator_bits(version, mode)

        if mode == Mode.NUMERIC:
            encoded_data = encode_numeric(data)
            char_count = len(data)
            prefix = ""
        elif mode == Mode.ALPHANUMERIC:
            encoded_data = encode_alphanumeric(data)
            char_count = len(data)
            prefix = ""
        else:
            encoded_data = encode_byte(data)
            # In Byte mode, character count indicator is the number of bytes
            char_count = len(data.encode("utf-8"))
            # ECI mode indicator 0111, Assignment 26 (UTF-8) as 8 bits
            prefix = f"{Mode.ECI.value:04b}{26:08b}" if use_eci else ""

        char_count_val = f"{char_count:0{char_count_bits}b}"
        total_bits = len(prefix) + len(mode_bits) + len(char_count_val) + len(encoded_data)

        # Calculate total data capacity for this version/EC level
        ec_info = EC_CONFIG[version][ec_level]
        total_data_codewords = sum(count * codewords for count, codewords in ec_info[1])
        total_data_bits = total_data_codewords * 8

        if total_bits <= total_data_bits:
            # Found suitable version. Complete bitstream with terminator and padding.
            bitstream = prefix + mode_bits + char_count_val + encoded_data

            # Terminator
            terminator_len = min(4, total_data_bits - len(bitstream))
            bitstream += "0" * terminator_len

            # Padding to multiple of 8
            while len(bitstream) % 8 != 0:
                bitstream += "0"

            # Padding codewords
            padding_bytes = [0xEC, 0x11]
            idx = 0
            while len(bitstream) < total_data_bits:
                bitstream += f"{padding_bytes[idx % 2]:08b}"
                idx += 1

            return version, mode, bitstream

    raise ValueError("Data too large for QR Version 10")

def bits_to_codewords(bitstream: str) -> List[int]:
    """Converts a bit string to a list of integer codewords."""
    codewords = []
    for i in range(0, len(bitstream), 8):
        codewords.append(int(bitstream[i:i+8], 2))
    return codewords

def interleave_blocks(version: int, ec_level: ErrorCorrectionLevel, data_codewords: List[int]) -> List[int]:
    """Interleaves data and error correction blocks."""
    from .rs import calculate_ec_codewords

    ec_info = EC_CONFIG[version][ec_level]
    ec_count_per_block = ec_info[0]

    data_blocks = []
    ec_blocks = []

    offset = 0
    for num_blocks, codewords_per_block in ec_info[1]:
        for _ in range(num_blocks):
            block = data_codewords[offset:offset+codewords_per_block]
            data_blocks.append(block)
            ec_blocks.append(calculate_ec_codewords(block, ec_count_per_block))
            offset += codewords_per_block

    # Interleave
    result = []
    max_data_len = max(len(b) for b in data_blocks)
    for i in range(max_data_len):
        for block in data_blocks:
            if i < len(block):
                result.append(block[i])

    for i in range(ec_count_per_block):
        for block in ec_blocks:
            result.append(block[i])

    return result
