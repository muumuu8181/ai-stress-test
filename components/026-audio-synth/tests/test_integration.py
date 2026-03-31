import pytest
import os
from audio_synth.sequencer import Sequencer
from audio_synth.envelope import ADSREnvelope
from audio_synth.filter import low_pass_filter
from audio_synth.wav_writer import save_wav


def test_full_synth_pipeline(tmp_path):
    sample_rate = 44100
    seq = Sequencer(sample_rate)
    env = ADSREnvelope(0.01, 0.05, 0.7, 0.1, sample_rate)

    # Melody: A4 (0.5s), R (0.1s), C5 (0.5s)
    melody = [("A4", 0.5), ("R", 0.1), ("C5", 0.5)]

    # 1. Render sequence
    buffer = seq.render(melody, waveform="square", envelope=env, amplitude=0.5)

    # 2. Filter buffer
    filtered = low_pass_filter(buffer, 1000, sample_rate)

    # 3. Save to WAV
    output_path = os.path.join(tmp_path, "melody.wav")
    save_wav(output_path, filtered, sample_rate)

    # 4. Verify output
    assert os.path.exists(output_path)
    assert len(filtered) == int(1.1 * sample_rate)
    # Check that amplitude is reduced by filter/envelope
    assert max(filtered) <= 0.5
    # Should have some sound (not all zero)
    assert any(abs(s) > 0.01 for s in filtered)


def test_synth_empty_input():
    seq = Sequencer(44100)
    buffer = seq.render([], waveform="sine")
    assert buffer == []


def test_synth_rest_only():
    seq = Sequencer(1000)
    buffer = seq.render([("R", 0.1)], waveform="sine")
    assert len(buffer) == 100
    assert all(s == 0.0 for s in buffer)
