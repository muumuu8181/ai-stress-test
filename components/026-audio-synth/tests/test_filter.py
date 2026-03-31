import pytest
from audio_synth.filter import low_pass_filter, high_pass_filter


def test_low_pass_filter_basic():
    # Simple DC-like signal
    buffer = [1.0] * 100
    # Very low cutoff should smooth it
    filtered = low_pass_filter(buffer, 10, 1000)
    assert filtered[0] < buffer[0]
    assert filtered[-1] > filtered[0]  # Rising towards 1.0


def test_high_pass_filter_basic():
    # Constant signal (DC)
    buffer = [1.0] * 100
    # High pass should remove DC
    filtered = high_pass_filter(buffer, 100, 1000)
    assert filtered[-1] < 0.1  # Should decay to 0


def test_filters_empty():
    assert low_pass_filter([], 100) == []
    assert high_pass_filter([], 100) == []


def test_filters_invalid_params():
    with pytest.raises(ValueError):
        low_pass_filter([1.0], 0)
    with pytest.raises(ValueError):
        low_pass_filter([1.0], -1)
    with pytest.raises(ValueError):
        low_pass_filter([1.0], 100, sample_rate=0)

    with pytest.raises(ValueError):
        high_pass_filter([1.0], 0)
    with pytest.raises(ValueError):
        high_pass_filter([1.0], -1)
    with pytest.raises(ValueError):
        high_pass_filter([1.0], 100, sample_rate=0)
