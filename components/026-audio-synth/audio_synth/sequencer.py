from typing import List, Tuple
from .notes import note_to_frequency
from .oscillator import Oscillator
from .envelope import ADSREnvelope


class Sequencer:
    """
    Sequences notes into a single audio buffer.
    """

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.oscillator = Oscillator(sample_rate)

    def render(
        self,
        sequence: List[Tuple[str, float]],
        waveform: str = "sine",
        envelope: ADSREnvelope = None,
        amplitude: float = 0.5,
    ) -> List[float]:
        """
        Renders a sequence of (note, duration) to a single audio buffer.

        Args:
            sequence: List of (note_name, duration_seconds).
                      If note_name is 'R', it's a rest.
            waveform: Oscillator waveform.
            envelope: Optional ADSR envelope.
            amplitude: Base amplitude.

        Returns:
            Rendered audio buffer.
        """
        full_buffer = []

        for note_name, duration in sequence:
            if duration < 0:
                raise ValueError(f"Negative duration {duration} for note {note_name}")

            if note_name == "R":
                # Rest
                num_samples = int(self.sample_rate * duration)
                full_buffer.extend([0.0] * num_samples)
            else:
                frequency = note_to_frequency(note_name)

                # If there's an envelope with a release, we may want to extend duration
                # For simplicity, let's keep the duration as requested,
                # but ensure release is part of it.

                note_buffer = self.oscillator.generate(
                    waveform=waveform,
                    frequency=frequency,
                    duration=duration,
                    amplitude=amplitude,
                )

                if envelope:
                    note_buffer = envelope.apply(note_buffer)

                full_buffer.extend(note_buffer)

        return full_buffer
