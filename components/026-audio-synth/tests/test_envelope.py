import pytest
from audio_synth.envelope import ADSREnvelope


def test_adsr_envelope_phases():
    sample_rate = 1000
    # A=0.1s, D=0.1s, S=0.5, R=0.1s
    # Attack samples: 100
    # Decay samples: 100
    # Release samples: 100
    envelope = ADSREnvelope(0.1, 0.1, 0.5, 0.1, sample_rate)

    # 500 samples (0.5s)
    buffer = [1.0] * 500
    shaped = envelope.apply(buffer)

    # 0 samples: 0.0 gain
    assert shaped[0] == 0.0
    # 100 samples (attack end): 1.0 gain
    assert shaped[100] == 1.0
    # 200 samples (decay end): 0.5 (sustain level)
    assert shaped[200] == 0.5
    # 400 samples (sustain phase): 0.5
    assert shaped[300] == 0.5
    assert shaped[400] == 0.5
    # 500 samples (release end): 0.0 gain
    assert shaped[499] < 0.05


def test_adsr_envelope_empty():
    envelope = ADSREnvelope(0.1, 0.1, 0.5, 0.1, 1000)
    assert envelope.apply([]) == []


def test_adsr_envelope_no_release():
    envelope = ADSREnvelope(0.1, 0.1, 0.5, 0.0, 1000)
    buffer = [1.0] * 500
    shaped = envelope.apply(buffer)
    # End of note should still be at sustain level
    assert shaped[499] == 0.5


def test_adsr_envelope_fast_release():
    envelope = ADSREnvelope(0.5, 0.5, 0.5, 0.5, 1000)
    # Total duration is only 0.2s (200 samples)
    # Release starts at sample 150? No, let's re-examine.
    # num_samples = 200, release_samples = 500.
    # note_on_duration = max(0, 200-500) = 0.
    # So it should start release immediately.
    buffer = [1.0] * 200
    shaped = envelope.apply(buffer)
    assert max(shaped) <= 0.5
