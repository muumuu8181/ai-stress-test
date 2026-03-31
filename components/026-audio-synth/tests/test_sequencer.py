import pytest
from audio_synth.sequencer import Sequencer
from audio_synth.envelope import ADSREnvelope


def test_sequencer_render():
    sample_rate = 1000
    seq = Sequencer(sample_rate)
    # 0.1s A4, 0.1s R, 0.1s C5
    melody = [("A4", 0.1), ("R", 0.1), ("C5", 0.1)]

    buffer = seq.render(melody, waveform="sine", amplitude=1.0)

    # 0.3s total = 300 samples
    assert len(buffer) == 300
    # First 100 samples (A4)
    assert any(abs(s) > 0.5 for s in buffer[:100])
    # Next 100 samples (Rest)
    assert all(s == 0.0 for s in buffer[100:200])
    # Next 100 samples (C5)
    assert any(abs(s) > 0.5 for s in buffer[200:])


def test_sequencer_with_envelope():
    sample_rate = 1000
    seq = Sequencer(sample_rate)
    env = ADSREnvelope(0.01, 0.01, 0.5, 0.01, sample_rate)
    melody = [("A4", 0.1)]

    buffer = seq.render(melody, waveform="sine", envelope=env, amplitude=1.0)
    assert buffer[0] == 0.0
    assert abs(buffer[10]) > 0.0  # Attack phase
