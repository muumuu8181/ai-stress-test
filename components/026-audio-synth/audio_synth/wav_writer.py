import wave
import struct
from typing import List


def save_wav(filepath: str, buffer: List[float], sample_rate: int = 44100):
    """
    Saves a float audio buffer to a 16-bit PCM WAV file.

    Args:
        filepath: Path to the WAV file.
        buffer: List of float samples (-1.0 to 1.0).
        sample_rate: Audio sample rate.
    """
    num_channels = 1
    sample_width = 2  # 16-bit

    with wave.open(filepath, "wb") as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)

        # Convert floats to 16-bit integers
        packed_data = []
        for sample in buffer:
            # Clipping (just in case)
            sample = max(-1.0, min(1.0, sample))
            # Scale to 16-bit range
            int_sample = int(sample * 32767)
            # Use little-endian signed short as required by WAV format
            packed_data.append(struct.pack("<h", int_sample))

        wav_file.writeframes(b"".join(packed_data))
