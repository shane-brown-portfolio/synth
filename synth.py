import argparse
import numpy as np
import sounddevice as sd

# Audio Generation Constants
SAMPLE_RATE = 48000
MAX_AMPLITUDE = 0.708


def note_to_frequency(note_number):
    """
    Convert MIDI note number to frequency.
    Uses A4 (440Hz) as reference note.
    """
    return 440.0 * (2 ** ((note_number - 69) / 12))


def generate_sawtooth(frequency, duration):
    """
    Generate a sawtooth waveform for a single note.
    Return a numpy array of audio samples.
    """
    sample_count = int(duration * SAMPLE_RATE)
    samples = np.arange(sample_count)

    waveform = (2 * ((samples * frequency / SAMPLE_RATE) % 1)) - 1

    return waveform * MAX_AMPLITUDE


def main():
    print("Personal MIDI Synth\n")

    frequency = note_to_frequency(69)
    samples = generate_sawtooth(frequency, 1)
    print("Generated samples:", len(samples))
    print("First 10 samples:")
    print(samples[:10])

if __name__ == "__main__":
    main()