from typing import List


class ADSREnvelope:
    """
    ADSR envelope to shape audio amplitude.
    """

    def __init__(
        self,
        attack: float,
        decay: float,
        sustain: float,
        release: float,
        sample_rate: int = 44100,
    ):
        """
        Initialize the ADSR envelope.

        Args:
            attack: Time to reach max amplitude in seconds.
            decay: Time to drop from max amplitude to sustain level in seconds.
            sustain: Sustain level (0.0 to 1.0).
            release: Time to drop from sustain level to zero in seconds.
            sample_rate: Audio sample rate.
        """
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
        self.sample_rate = sample_rate

    def apply(self, buffer: List[float]) -> List[float]:
        """
        Applies the ADSR envelope to an audio buffer.
        Note: The buffer length is expected to include the release portion if needed.

        Args:
            buffer: Audio samples.

        Returns:
            Shaped audio samples.
        """
        if not buffer:
            return []

        num_samples = len(buffer)
        attack_samples = int(self.attack * self.sample_rate)
        decay_samples = int(self.decay * self.sample_rate)
        release_samples = int(self.release * self.sample_rate)

        # Sustain starts after attack and decay
        # Note: if the buffer is shorter than attack + decay, we compress the phases.
        # But for now let's assume buffer is long enough or adjust.

        shaped_buffer = [0.0] * num_samples

        # The actual note duration (where it's "held") is num_samples - release_samples
        note_on_duration_samples = max(0, num_samples - release_samples)

        for i in range(num_samples):
            # Attack phase
            if i < attack_samples and i < note_on_duration_samples:
                gain = i / attack_samples
            # Decay phase
            elif i < (attack_samples + decay_samples) and i < note_on_duration_samples:
                decay_pos = i - attack_samples
                gain = 1.0 - (1.0 - self.sustain) * (decay_pos / decay_samples)
            # Sustain phase
            elif i < note_on_duration_samples:
                gain = self.sustain
            # Release phase
            else:
                release_pos = i - note_on_duration_samples
                if release_samples > 0:
                    # Start release from the current gain if it was released before finishing attack/decay
                    # For simplicity, assume it reached sustain level.
                    gain = self.sustain * (1.0 - release_pos / release_samples)
                    gain = max(0.0, gain)
                else:
                    gain = 0.0

            shaped_buffer[i] = buffer[i] * gain

        return shaped_buffer
