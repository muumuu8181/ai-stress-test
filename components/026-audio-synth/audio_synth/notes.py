import math
from typing import Dict


def note_to_frequency(note: str) -> float:
    """
    Converts a note string (e.g., 'C4', 'D#5', 'Bb3') to its frequency in Hz.
    Reference: C4 = 261.63Hz, A4 = 440Hz.

    Args:
        note: Note string.

    Returns:
        Frequency in Hz.

    Raises:
        ValueError: If the note format is invalid.
    """
    notes_map: Dict[str, int] = {
        "C": 0,
        "C#": 1,
        "Db": 1,
        "D": 2,
        "D#": 3,
        "Eb": 3,
        "E": 4,
        "F": 5,
        "F#": 6,
        "Gb": 6,
        "G": 7,
        "G#": 8,
        "Ab": 8,
        "A": 9,
        "A#": 10,
        "Bb": 10,
        "B": 11,
    }

    if not note or len(note) < 2:
        raise ValueError(f"Invalid note format: {note}")

    name = note[:-1]
    try:
        octave = int(note[-1])
    except ValueError:
        # Support two digit octaves if needed, but standard is 1 digit
        # Let's try to handle cases like "C10"
        if note[-2:].isdigit():
            name = note[:-2]
            octave = int(note[-2:])
        else:
            raise ValueError(f"Invalid octave in note: {note}")

    if name not in notes_map:
        # Check if it was something like "C#10" where name was incorrectly split
        if len(note) >= 3 and note[-2:].isdigit():
            name = note[:-2]
            octave = int(note[-2:])

        if name not in notes_map:
            raise ValueError(f"Invalid note name: {name}")

    # A4 is 440Hz, which is 9 semitones above C4.
    # C4 is the 4th octave.
    # Frequency = 440 * 2^((n - 69) / 12) where n is MIDI note number
    # MIDI note for C4 is 60.

    semitone = notes_map[name]
    midi_note = (octave + 1) * 12 + semitone

    # Using C4 = 261.63Hz as reference (which corresponds to A4 = 440Hz approx)
    # 440 * 2^((60-69)/12) = 440 * 2^(-9/12) = 261.625...

    frequency = 440.0 * math.pow(2.0, (midi_note - 69) / 12.0)
    return round(frequency, 2)
