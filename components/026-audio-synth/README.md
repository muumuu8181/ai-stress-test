# Audio Synthesizer (WAV output)

A pure Python audio synthesizer that generates WAV files from note sequences.

## Features

- **Waveform Generation**: Sine, Square, Sawtooth, Triangle, and Noise.
- **ADSR Envelope**: Control Attack, Decay, Sustain, and Release phases.
- **Oscillator Layering**: Mix multiple oscillators for complex sounds.
- **Filters**: Simple Low-pass and High-pass filters.
- **Note Notation**: Use standard musical notation (e.g., "C4", "D#5", "Bb3").
- **Sequencer**: Define melodies as a sequence of notes and durations.
- **WAV Export**: Save audio to 16-bit PCM WAV files.

## Installation

No external dependencies are required. Just Python 3.x.

## Usage Example

```python
from audio_synth.sequencer import Sequencer
from audio_synth.envelope import ADSREnvelope
from audio_synth.filter import low_pass_filter
from audio_synth.wav_writer import save_wav

# Initialize sample rate
sample_rate = 44100

# Define an ADSR Envelope
# Attack: 0.1s, Decay: 0.2s, Sustain: 0.6, Release: 0.3s
envelope = ADSREnvelope(0.1, 0.2, 0.6, 0.3, sample_rate)

# Define a melody (Note, Duration in seconds)
melody = [
    ("C4", 0.5),
    ("E4", 0.5),
    ("G4", 0.5),
    ("C5", 1.0),
    ("R", 0.2), # Rest
    ("G4", 0.5),
    ("C4", 1.0)
]

# Render melody using the sequencer
sequencer = Sequencer(sample_rate)
audio_buffer = sequencer.render(
    melody,
    waveform='sine',
    envelope=envelope,
    amplitude=0.5
)

# Apply a low-pass filter (cutoff 1000Hz)
filtered_buffer = low_pass_filter(audio_buffer, 1000, sample_rate)

# Save to WAV file
save_wav("melody.wav", filtered_buffer, sample_rate)
```

## API Reference

### `notes.note_to_frequency(note: str) -> float`
Converts a note string to its frequency in Hz.

### `oscillator.Oscillator(sample_rate: int)`
Class for generating waveforms.
- `generate(waveform, frequency, duration, amplitude, phase) -> List[float]`

### `envelope.ADSREnvelope(attack, decay, sustain, release, sample_rate)`
Class for applying ADSR envelopes.
- `apply(buffer: List[float]) -> List[float]`

### `filter.low_pass_filter(buffer, cutoff_freq, sample_rate)`
Applies a first-order low-pass filter.

### `filter.high_pass_filter(buffer, cutoff_freq, sample_rate)`
Applies a first-order high-pass filter.

### `wav_writer.save_wav(filepath, buffer, sample_rate)`
Saves the audio buffer to a WAV file.

### `sequencer.Sequencer(sample_rate)`
Class for rendering note sequences.
- `render(sequence, waveform, envelope, amplitude) -> List[float]`

## Testing

Run tests using pytest:
```bash
pytest tests/
```
