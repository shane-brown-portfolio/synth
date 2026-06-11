import argparse
import numpy as np
import sounddevice as sd
import mido

# Audio settings
SAMPLE_RATE = 48000
MAX_AMPLITUDE = 0.708

# Envelope settings (10 ms attack, 10 ms release)
ATTACK_TIME = 0.01
RELEASE_TIME = 0.01

# Amount the envelope changes each sample
ATTACK_STEP = 1 / (ATTACK_TIME * SAMPLE_RATE)
RELEASE_STEP = 1 / (RELEASE_TIME * SAMPLE_RATE)


def note_to_frequency(note_number):
    """
    Convert MIDI note number to frequency.
    Uses A4 (440Hz) as reference note.
    """
    return 440.0 * (2 ** ((note_number - 69) / 12))


class Synth:
    def __init__(self):
        self.curr_frequency = None      # Current note frequency
        self.phase = 0.0                # Current position in the waveform
        self.envelope_level = 0.0       # Current volume level (0.0 to 1.0)
        self.releasing = False          # True when the note is being released
    
    def generate_sawtooth(self, frames):
        """
        Generate a block of sawtooth samples for the given number of frames.
        Return a numpy array of audio samples.
        """
        sample_numbers = np.arange(frames)

        # Generate a sawtooth wave between -1 and 1
        waveform = (
            (self.phase + self.curr_frequency * sample_numbers / SAMPLE_RATE) % 1
        ) * 2 - 1

        # Save the waveform position for the next callback
        self.phase = (self.phase + self.curr_frequency * frames / SAMPLE_RATE) % 1

        # Scale to -3 dBFS
        return waveform * MAX_AMPLITUDE
    
    def apply_envelope(self, samples):
        """
        Apply the attack/release envelope to a block of samples.

        Attack: Volume increases from 0 to 100% over ATTACK_TIME.
        Release: Volume decreases from 100% to 0 over RELEASE_TIME.

        Returns the audio samples after applying the envelope.
        """
        output_samples = np.empty_like(samples)

        for i in range(len(samples)):

            # Increase volume during attack
            if not self.releasing:
                self.envelope_level += ATTACK_STEP

            # Decrease volume during release
            else:
                self.envelope_level -= RELEASE_STEP

            # Keep the envelope between 0 and 1
            self.envelope_level = np.clip(self.envelope_level, 0.0, 1.0)

            output_samples[i] = samples[i] * self.envelope_level

        return output_samples
    
    def note_on(self, note_number):
        """ Start playing a note. """
        self.curr_frequency = note_to_frequency(note_number)
        self.envelope_level = 0.0
        self.releasing = False

    def note_off(self):
        """ Begin the release portion of the envelope for the current note. """
        self.releasing = True

    def audio_callback(self, outdata, frames, time, status):
        """ Generate audio for the next output block. """
        
        # Output silence when nothing is playing
        if self.curr_frequency is None and self.envelope_level <= 0:
            outdata.fill(0)
            return

        # Generate the sawtooth waveform and apply the envelope
        samples = self.generate_sawtooth(frames)
        samples = self.apply_envelope(samples)

        outdata[:, 0] = samples

        # Stop the note when release reaches zero
        if self.releasing and self.envelope_level <= 0:
            self.curr_frequency = None
            self.releasing = False


def main():
    parser = argparse.ArgumentParser(
        description="MIDI Synthesizer"
    )

    parser.add_argument(
        "--midi-device",
        help="Name of the MIDI input device to use"
    )

    args = parser.parse_args()

    print("MIDI Synthesizer\n")

    input_devices = mido.get_input_names()

    if not input_devices:
        print("No MIDI devices found.")
        return
    
    # Display all available MIDI input devices
    print("Available MIDI Input Devices:")
    for device in input_devices:
        print(f"  {device}")

    if args.midi_device:
        # Verify that the requested device exists
        if args.midi_device not in input_devices:
            print(f"\nError: MIDI device '{args.midi_device}' not found.")
            return

        input_name = args.midi_device

    else:
        # Use the first available MIDI device by default
        input_name = input_devices[0]
    
    print(f"\nUsing MIDI device: {input_name}")

    # Declare synthesizer instance
    synth = Synth()

    with sd.OutputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        callback=synth.audio_callback
    ):
        print("\nWaiting for MIDI input... (Press Ctrl+C to quit)\n")

        try:
            with mido.open_input(input_name) as midi_input:
                for message in midi_input:
                    print(message)

                    # Start note
                    if message.type == "note_on" and message.velocity > 0:
                        synth.note_on(message.note)

                    # End note
                    elif (
                        message.type == "note_off"
                        or (message.type == "note_on" and message.velocity == 0)
                    ):
                        synth.note_off()

        except KeyboardInterrupt:
            print("\nExiting synthesizer...")


if __name__ == "__main__":
    main()