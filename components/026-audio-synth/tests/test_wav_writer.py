import os
import wave
import pytest
from audio_synth.wav_writer import save_wav


def test_save_wav_header_verification(tmp_path):
    filepath = os.path.join(tmp_path, "test.wav")
    buffer = [0.0, 0.5, 1.0, -1.0, -0.5]
    sample_rate = 44100
    save_wav(filepath, buffer, sample_rate)

    assert os.path.exists(filepath)

    with wave.open(filepath, "rb") as wav_file:
        assert wav_file.getnchannels() == 1
        assert wav_file.getsampwidth() == 2  # 16-bit
        assert wav_file.getframerate() == sample_rate
        assert wav_file.getnframes() == len(buffer)

        # Verify first few samples
        frames = wav_file.readframes(len(buffer))
        import struct

        # 'h' is 16-bit signed integer
        data = struct.unpack(f"{len(buffer)}h", frames)
        assert data[0] == 0
        assert data[1] == int(0.5 * 32767)
        assert data[2] == 32767
        assert data[3] == -32767
        assert data[4] == int(-0.5 * 32767)
