# MIDI Synthesizer

This project implements a simple monophonic MIDI synthesizer that accepts MIDI note events from a connected controller and generates audio in real time using software synthesis. The program converts MIDI note messages into frequencies, generates sawtooth waveforms, applies an attack-release envelope, and outputs the resulting audio through the system speakers.

The synthesizer provides:

- Monophonic playback (one note at a time)
- Sawtooth waveform synthesis
- A fixed attack-release (AR) envelope
- Real-time audio output
- MIDI controller selection using a command-line argument

The synthesizer responds to:

- **Note On** messages to begin playing a note
- **Note Off** messages to release the note
- **Note On messages with velocity 0**, which are treated as Note Off events

## Build Instructions

### Requirements

- Python 3.x
- numpy
- sounddevice
- mido
- python-rtmidi

### Install Dependencies

```bash
pip install numpy sounddevice mido python-rtmidi
```

Or:

```bash
pip install -r requirements.txt
```

### Run

Start the synthesizer:

```bash
python3 synth.py
```

The following command-line arguments are available:

| Argument | Description |
|------------|------------|
| `--midi-device DEVICE` | Connect directly to a specific MIDI input device. |

Example:

```bash
python3 synth.py --midi-device "MIDI Keyboard"
```

If no device is specified, the program displays all available MIDI input devices and automatically selects the first one.

## Output

After running the program:

- Available MIDI input devices are displayed
- A MIDI controller is selected
- Audio output begins through the speakers
- Incoming MIDI messages are displayed in the terminal
- Notes are synthesized and played in real time
- The program continues running until interrupted with Ctrl+C

## How It Works

This program converts MIDI note events into audio using waveform synthesis and an attack-release envelope.

1. **Receive MIDI Events**

   The program opens a MIDI input device using `mido`.
   - When a key is pressed:
     - A `note_on` event starts a note.
   - When a key is released:
     - A `note_off` event begins the release stage.

   Some MIDI controllers send `note_on velocity=0` instead of separate `note_off` messages. These events are treated as note releases.

2. **Convert MIDI Notes to Frequencies**
   
   Incoming MIDI note numbers are converted into frequencies using equal temperament with A4 as the reference note:

   ```python
   frequency = 440 * (2 ** ((note - 69) / 12))
   ```

3. **Generate Sawtooth Waveform**

   The synthesizer generates a sawtooth waveform in real time.

   The waveform oscillates between -1 and 1 and is scaled to approximately -3 dBFS:

   ```python
   amplitude = 0.708
   ```

   Waveform phase is preserved between audio callbacks to maintain continuous playback.

4. **Apply the Attack-Release Envelope**

   Each note uses a fixed envelope:
   - Attack time: 10 milliseconds
   - Release time: 10 milliseconds

   During attack, the volume increases linearly from silence to full volume.
   During release, the volume decreases linearly back to silence.

5. **Output Audio**

   The program uses `sounddevice.OutputStream()` to continuously request blocks of audio samples.

   For each callback:
   1. Generate a block of sawtooth samples.
   2. Apply the attack-release envelope.
   3. Send the samples to the output device.

   This process repeats continuously while the program is running.

## How It Went

Overall, the project went well once I understood how MIDI input and audio callbacks interact.

One of the more interesting challenges was learning how real-time audio differs from generating an entire sound file at once. Instead of producing all samples ahead of time, the synthesizer continuously generates small blocks of audio whenever the output stream requests them. This initially caused some confusion because I was trying to generate and play notes individually, which resulted in noticeable playback and interaction latency in the program.

Another challenge was organizing the program state. Initially, I used several global variables to track the current note, envelope, and waveform position while experimenting with `sounddevice.OutputStream()` and the audio callback function. As the project grew, this became difficult to manage. Refactoring the program into a `Synth` class simplified the design by keeping all synthesizer state and behavior together.

During development, using VMPK made it possible to test MIDI input without requiring dedicated hardware. It also helped isolate issues while implementing the audio callback and attack-release envelope behavior.

## Still To Be Done

Several possible improvements include features such as:

- Add support for additional waveforms such as sine, square, and triangle waves
- Support MIDI velocity to control note volume
- Implement ADSR envelopes with decay and sustain stages
- Add a white noise source to the synthesizer with its own envelope
- Add polyphony so multiple notes can play simultaneously
- Add MIDI control-change (CC) support

These improvements would make the synthesizer more expressive and provide functionality closer to modern software synthesizers.
