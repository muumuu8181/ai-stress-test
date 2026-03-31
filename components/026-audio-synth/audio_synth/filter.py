import math
from typing import List


def low_pass_filter(
    buffer: List[float], cutoff_freq: float, sample_rate: int = 44100
) -> List[float]:
    """
    Applies a simple first-order low-pass filter.

    Args:
        buffer: Audio samples.
        cutoff_freq: Cutoff frequency in Hz.
        sample_rate: Sample rate.

    Returns:
        Filtered audio samples.
    """
    if not buffer:
        return []

    # RC filter time constant
    dt = 1.0 / sample_rate
    rc = 1.0 / (2.0 * math.pi * cutoff_freq)
    alpha = dt / (rc + dt)

    filtered_buffer = [0.0] * len(buffer)
    prev_val = 0.0
    for i, val in enumerate(buffer):
        filtered_buffer[i] = prev_val + alpha * (val - prev_val)
        prev_val = filtered_buffer[i]

    return filtered_buffer


def high_pass_filter(
    buffer: List[float], cutoff_freq: float, sample_rate: int = 44100
) -> List[float]:
    """
    Applies a simple first-order high-pass filter.

    Args:
        buffer: Audio samples.
        cutoff_freq: Cutoff frequency in Hz.
        sample_rate: Sample rate.

    Returns:
        Filtered audio samples.
    """
    if not buffer:
        return []

    # RC filter time constant
    dt = 1.0 / sample_rate
    rc = 1.0 / (2.0 * math.pi * cutoff_freq)
    alpha = rc / (rc + dt)

    filtered_buffer = [0.0] * len(buffer)
    prev_val = 0.0
    prev_orig = 0.0
    for i, val in enumerate(buffer):
        filtered_buffer[i] = alpha * (prev_val + val - prev_orig)
        prev_val = filtered_buffer[i]
        prev_orig = val

    return filtered_buffer
