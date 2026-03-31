import pytest
from audio_synth.notes import note_to_frequency


def test_note_to_frequency_basic():
    assert note_to_frequency("A4") == 440.0
    # C4 = 261.63Hz
    assert note_to_frequency("C4") == 261.63
    # A3 = 220Hz
    assert note_to_frequency("A3") == 220.0
    # C5 = 523.25
    assert note_to_frequency("C5") == 523.25


def test_note_to_frequency_sharps_flats():
    # C#4 == Db4
    assert note_to_frequency("C#4") == note_to_frequency("Db4")
    # A#4 == Bb4
    assert note_to_frequency("A#4") == note_to_frequency("Bb4")
    assert note_to_frequency("A#4") == 466.16


def test_note_to_frequency_invalid():
    with pytest.raises(ValueError):
        note_to_frequency("X4")
    with pytest.raises(ValueError):
        note_to_frequency("C")
    with pytest.raises(ValueError):
        note_to_frequency("")


def test_note_to_frequency_octaves():
    # Test multi-digit octave
    assert note_to_frequency("C10") > note_to_frequency("C9")
    assert note_to_frequency("C#10") > note_to_frequency("C10")


def test_note_to_frequency_invalid_extra():
    with pytest.raises(ValueError):
        note_to_frequency("C#Z")
    with pytest.raises(ValueError):
        note_to_frequency("CZ10")
