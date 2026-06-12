# Just intonation classes
[![Actions Status](https://github.com/endolith/just_intonation/workflows/Python%20package/badge.svg)](https://github.com/endolith/just_intonation/actions) [![codecov](https://codecov.io/gh/endolith/just_intonation/branch/master/graph/badge.svg?token=QQDWWPXA22)](https://codecov.io/gh/endolith/just_intonation)

This module provides pure Python classes for experimenting with [Just intonation](https://en.wikipedia.org/wiki/Just_intonation) (music made from frequency ratio relationships rather than equal divisions of the octave):

* `Interval(numerator, denominator)` - Represents musical [interval ratios](https://en.wikipedia.org/wiki/Interval_ratio)/[rational intervals](https://en.xen.wiki/w/Interval), a relative step between pitches
  * `.numerator` - Numerator after reducing to simplest form
  * `.denominator` - Denominator after reducing to simplest form
  * `.complement` - The [inversion](https://en.wikipedia.org/wiki/Inversion_%28music%29#Intervals) or [octave complement](https://en.xen.wiki/w/Octave_complement) of the interval (P4 → P5, etc.)
  * `.odd_limit` - [The smallest odd limit of an interval](https://en.xen.wiki/w/Odd_limit#Odd_limit_of_a_ratio)
  * `.prime_limit` - [Prime limit or harmonic limit of an interval](https://en.xen.wiki/w/Harmonic_limit)
  * `.kees_height` - [Kees semi-height](https://en.xen.wiki/w/Kees_semi-height)
  * `.benedetti_height` - [Benedetti height](https://en.xen.wiki/w/Benedetti_height)
  * `.tenney_height` - [Tenney height](https://en.xen.wiki/w/Tenney_height)
  * Mathematical operations like addition of intervals, multiplication by integers, etc.
* Convenience intervals
  * `P1` - Unison
  * `m2` - Minor second
  * `M2` - Major second
  * `m3` - Minor third
  * `M3` - Major third
  * `P4` - Perfect fourth
  * `P5` - Perfect fifth
  * etc.
* `Chord(4, 5, 6)`, `Chord(Interval('M3'), Interval('P5'))`, etc. - Class that represents chords/triads, a combination of multiple intervals
  * `.terms` - List of terms in the frequency ratio that makes up the chord
  * `.intervals` - List of musical intervals that make up the chord, relative to the root
  * `.steps` - List of musical intervals which, stacked together, produce the chord
  * `.all_steps` - Set of all music intervals that can be made by any tone in the chord with any other tone
  * `.odd_limit` - The [intervallic odd-limit](https://en.xen.wiki/w/Odd_limit#Relationship_to_other_limits)
  * `.prime_limit` - The highest prime limit of any interval found in the Chord
  * `.inversion(n)` - The *n*th inversion of a chord
* `Pitch(frequency)` - Class that represents absolute frequencies
  * `.frequency` - Value of the frequency in hertz

Probably all of this is redundant with [Scala](http://www.huygens-fokker.org/scala/), but

1. I don't know how to use it.
2. I wanted to learn by doing:
   - Just Intonation
   - Object-oriented Python
   - Unit testing

## Usage

```py
>>> Chord(4, 5, 6).intervals
(Interval(5, 4), Interval(3, 2))

>>> M3 + m3
Interval(3, 2)

>>> Interval('P5').complement == P4
True

>>> Pitch(440) + P5
Pitch(660)
```

## Installation

One possibility is to install with pip from GitHub:

    pip install git+https://github.com/endolith/just_intonation.git

## MIDI playback (`midi_play.py`)

`midi_play.py` is a small **demo / scratchpad**, not part of the installable
`just_intonation` package. It sends notes to a **MIDI output port** using
[mido](https://mido.readthedocs.io/) with the **[RtMidi](https://www.music.mcgill.ca/~gary/rtmidi/)**
backend (`python-rtmidi`). It does **not** produce audio by itself: you need a
**second program** (a DAW, standalone synth, or similar) that listens on the
**other end** of a **virtual MIDI cable**.

Rough signal path:

```text
midi_play.py  --MIDI-->  virtual cable  --MIDI-->  softsynth / DAW  -->  audio
```

### Why setup is fiddly

* The script used to assume **device id `3`** (pygame / PortMidi) and a name containing **`LoopBe`**. Port and index order still change when drivers or USB gear change; it now **scans** RtMidi output port **names** by default (see environment variables below).
* **Pitch bend** is per **MIDI channel**. The script cycles channels so chords stay bent independently; channel **10** (GM drums) is skipped.
* You must hear the **same synth** that receives the cable. If nothing is routed to the cable’s **input** side, you get silence even though the script runs.

### Dependencies

```bash
pip install -r requirements-midi.txt
```

That installs **mido** with the **RtMidi** port driver and **numpy** (only used
for the `lydian` / `locrian` mode arrays at import time). The main library and
CI tests do not require these packages.

### Windows — LoopBe1 or loopMIDI

1. Install a virtual MIDI driver, for example **[LoopBe1](https://www.tobias-erichsen.de/software/loopbe1.html)** (free for non‑commercial use) or **loopMIDI** from the same author.
2. After installation you should see an **output** port in Windows whose name contains `LoopBe` (e.g. **“LoopBe Internal MIDI”**). `midi_play.py` looks for that substring by default.
3. Open your **synthesizer** (Reaper, Ableton, standalone VST host, etc.) and set its **MIDI input** to that **same** LoopBe / loopMIDI port (the “other end” of the cable).
4. Run Python from the repo root so `just_intonation` imports correctly, e.g.:

   ```bash
   python -i midi_play.py
   ```

   Then call `just_major()`, `play_chord(...)`, etc. in the REPL.

### macOS — IAC Driver

1. Open **Audio MIDI Setup** → **Window** → **Show MIDI Studio** → double‑click **IAC Driver** → enable **“Device is online”** and at least one **port** (e.g. **Bus 1**).
2. Point your synth’s **MIDI input** at that IAC bus.
3. Set a match substring for this script, for example:

   ```bash
   export JUST_INTONATION_MIDI_OUT_NAME=IAC
   python -i midi_play.py
   ```

### Linux — ALSA virtual port + `aconnect`

Typical pattern: create a writable **MIDI Through** or **virmidi** port, run
**FluidSynth** / **TiMidity++** / etc., then connect with **`aconnect`**:

```bash
# Example: FluidSynth with ALSA; names vary by distro / args.
fluidsynth -a alsa -m alsa_seq /path/to/soundfont.sf2 &
python -i midi_play.py &
# List clients, then connect this script’s MIDI output client to FluidSynth:
aconnect -l
aconnect <pygame_sender> <fluidsynth_receiver>
```

Exact client numbers change every run; use `aconnect -l` after starting both
ends. If `mido.get_output_names()` lists **“Midi Through Port-0”** as an output, you can try:

```bash
export JUST_INTONATION_MIDI_OUT_NAME="Midi Through"
```

…and wire the other program accordingly (some setups route **Through**
between apps; others need **virmidi** — see your distro’s MIDI how‑tos).

### Choosing the device from Python

If auto‑detection picks the wrong port:

1. Run once without fixing anything; the **`RuntimeError`** lists **all** MIDI
   **output** port names mido sees, with numeric indices.
2. Pin the id:

   ```bash
   export JUST_INTONATION_MIDI_DEVICE_ID=5
   python -i midi_play.py
   ```

3. Or match a unique substring of the port name (case‑insensitive):

   ```bash
   export JUST_INTONATION_MIDI_OUT_NAME=loopmidi
   ```

Other backends (PortMidi, etc.) are available in mido but not used by this
script; see [mido backends](https://mido.readthedocs.io/en/stable/backends/index.html).

### Pitch‑bend detail

The script rounds each frequency to the nearest **MIDI note number**, then
applies a **pitch wheel** offset for the remaining fraction of a semitone.
Your synth should use the **default** bend range (**±2 semitones**); if it is
configured differently, bends will sound wrong.

(Earlier versions of this demo used **pygame** / PortMidi; pitch bend support
landed upstream in pygame after [PR #394](https://github.com/pygame/pygame/pull/394).)

## Examples

* [Everything is a power chord in just intonation](https://soundcloud.com/endolith/everything-is-a-power-chord-in-just-intonation) - Dyads made from the harmonic series, first in piano, then undistorted guitar, then distorted guitar.
* [Enumerating the rationals](https://soundcloud.com/endolith/enumerating-the-rationals) - A small portion of the Calkin-Wilf sequence, played on a fractal piano with an infinite number of keys.
