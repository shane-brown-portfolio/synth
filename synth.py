import argparse
import numpy as np
import sounddevice as sd
import mido

# Audio Generation Constants
SAMPLE_RATE = 48000
MAX_AMPLITUDE = 0.708

ATTACK_TIME = 0.01
RELEASE_TIME = 0.01


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


def play_audio(audio):
    """Play generated audio through speakers."""
    sd.play(audio, SAMPLE_RATE)


def apply_envelope(samples):
    """
    Apply a fixed attack-release envelope.

    Attack: Volume increases from 0 to 100% over the first 10 milliseconds.
    Release: Volume decreases from 100% to 0 over the last 10 milliseconds.

    Returns the scaled audio samples by the envelope values.
    """

    # Convert attack/release times to sample counts
    attack_samples = int(ATTACK_TIME * SAMPLE_RATE)
    release_samples = int(RELEASE_TIME * SAMPLE_RATE)

    envelope = np.ones(len(samples)) # Full volume

    # Linear fade-in
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

    # Linear fade-out
    envelope[-release_samples:] = np.linspace(1, 0, release_samples)

    return samples * envelope


def main():
    print("MIDI Synthesizer\n")
    print("Available MIDI Input Devices:")

    input_devices = mido.get_input_names()

    if not input_devices:
        print("No MIDI devices found.")
        return

    for device in input_devices:
        print(device)
    
    print("\nWaiting for MIDI input...\n")

    # Open the first available MIDI input device
    input_name = input_devices[0]
    print(f"Using MIDI device: {input_name}")

    with mido.open_input(input_name) as port:
        for message in port:
            print(message)

            # Start note
            if (message.type == "note_on" and message.velocity > 0):
                frequency = note_to_frequency(message.note)
                samples = generate_sawtooth(frequency, 0.5)

                samples = apply_envelope(samples)
                play_audio(samples)

            # End note
            elif (message.type == "note_off"
                or (message.type == "note_on" and message.velocity == 0)):
                sd.stop()


if __name__ == "__main__":
    main()