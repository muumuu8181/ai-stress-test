import math
import pytest
from audio_synth.oscillator import Oscillator, mix_oscillators


def test_oscillator_sine_frequency():
    sample_rate = 44100
    osc = Oscillator(sample_rate)
    frequency = 1000.0
    duration = 0.01  # 441 samples

    samples = osc.generate("sine", frequency, duration, amplitude=1.0)
    assert len(samples) == int(sample_rate * duration)

    # Check periodicity
    # At 1000Hz, the period is 1ms or 44.1 samples
    # The first peak should be at 1/4 of a period: 44.1 / 4 ~= 11 samples
    # sine(2*pi*f*t) is 1.0 when 2*pi*f*t = pi/2 -> t = 1/(4f) = 1/4000 = 0.00025s
    # i = t * sample_rate = 0.00025 * 44100 = 11.025 samples.
    # samples[11] should be near 1.0
    assert samples[11] > 0.99


def test_oscillator_square():
    osc = Oscillator(44100)
    samples = osc.generate("square", 1000, 0.01, amplitude=0.5)
    for s in samples:
        assert abs(s) == 0.5


def test_oscillator_triangle():
    osc = Oscillator(44100)
    samples = osc.generate("triangle", 1000, 0.01, amplitude=1.0)
    assert max(samples) <= 1.0
    assert min(samples) >= -1.0


def test_oscillator_sawtooth():
    osc = Oscillator(44100)
    samples = osc.generate("sawtooth", 1000, 0.01, amplitude=1.0)
    assert max(samples) <= 1.0
    assert min(samples) >= -1.0


def test_oscillator_noise():
    osc = Oscillator(44100)
    samples = osc.generate("noise", 0, 0.01, amplitude=1.0)
    assert len(samples) == 441
    # Check it's random-ish
    assert samples[0] != samples[1]


def test_mix_oscillators():
    buf1 = [0.5, 0.5, 0.5]
    buf2 = [0.2, 0.2, 0.2]
    mixed = mix_oscillators([buf1, buf2])
    assert mixed == [0.7, 0.7, 0.7]


def test_mix_oscillators_clipping():
    buf1 = [0.8, 0.8, 0.8]
    buf2 = [0.5, 0.5, 0.5]
    mixed = mix_oscillators([buf1, buf2])
    assert mixed == [1.0, 1.0, 1.0]


def test_oscillator_invalid_waveform():
    osc = Oscillator(44100)
    with pytest.raises(ValueError):
        osc.generate("invalid", 1000, 0.1)
