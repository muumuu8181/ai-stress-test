import math
import random
from typing import List, Optional


class Oscillator:
    """
    Audio oscillator to generate various waveforms.
    """

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def generate(
        self,
        waveform: str,
        frequency: float,
        duration: float,
        amplitude: float = 0.5,
        phase: float = 0.0,
    ) -> List[float]:
        """
        Generates a buffer of audio samples.

        Args:
            waveform: 'sine', 'square', 'sawtooth', 'triangle', 'noise'.
            frequency: Frequency in Hz.
            duration: Duration in seconds.
            amplitude: Amplitude (0.0 to 1.0).
            phase: Initial phase in radians.

        Returns:
            List of float samples.
        """
        num_samples = int(self.sample_rate * duration)
        samples = []

        for i in range(num_samples):
            t = i / self.sample_rate
            if waveform == "sine":
                val = math.sin(2 * math.pi * frequency * t + phase)
            elif waveform == "square":
                val = (
                    1.0 if math.sin(2 * math.pi * frequency * t + phase) >= 0 else -1.0
                )
            elif waveform == "sawtooth":
                # Sawtooth wave: 2 * (t * f % 1) - 1
                val = 2.0 * ((t * frequency + phase / (2 * math.pi)) % 1.0) - 1.0
            elif waveform == "triangle":
                # Triangle wave: 2 * abs(2 * (t * f % 1) - 1) - 1
                val = (
                    2.0
                    * abs(2.0 * ((t * frequency + phase / (2 * math.pi)) % 1.0) - 1.0)
                    - 1.0
                )
            elif waveform == "noise":
                val = random.uniform(-1.0, 1.0)
            else:
                raise ValueError(f"Unknown waveform: {waveform}")

            samples.append(val * amplitude)

        return samples


def mix_oscillators(buffers: List[List[float]]) -> List[float]:
    """
    Mixes multiple audio buffers by summing them.

    Args:
        buffers: List of audio buffers (list of floats).

    Returns:
        Mixed audio buffer.
    """
    if not buffers:
        return []

    max_len = max(len(b) for b in buffers)
    mixed = [0.0] * max_len

    for buffer in buffers:
        for i, val in enumerate(buffer):
            mixed[i] += val

    # Clipping
    for i in range(max_len):
        if mixed[i] > 1.0:
            mixed[i] = 1.0
        elif mixed[i] < -1.0:
            mixed[i] = -1.0

    return mixed
