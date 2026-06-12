# -*- coding: utf-8 -*-
"""
Play just-intonation material over MIDI using pitch bend.

Each note uses its own MIDI channel so polyphony can stay in tune: the
script picks the nearest MIDI note number and applies a small pitch-bend
offset for the remaining cents.

MIDI I/O uses `mido` with the **RtMidi** backend (`pip install mido[ports-rtmidi]`).
You send messages from this script into a *virtual MIDI cable* (or similar),
and a separate synthesizer listens on the other end.

See README.md (MIDI playback) for LoopBe / IAC / Linux routing and the
``JUST_INTONATION_*`` environment variables.
"""

from __future__ import division, print_function

import atexit
import os
import time
import random
import math
from threading import Timer

import mido

mido.set_backend('mido.backends.rtmidi')

from numpy import arange

from just_intonation import Interval, Pitch, Chord, m3, M3, P4, P5, P8


def _list_midi_output_names():
    """Return output port names (RtMidi / mido order)."""
    try:
        return list(mido.get_output_names())
    except Exception as exc:
        raise RuntimeError(
            'Could not list MIDI output ports (RtMidi failed during '
            'enumeration). On Linux, ensure the ALSA sequencer is available '
            '(often /dev/snd/seq) and ALSA MIDI packages are installed. '
            'Original error:\n%s' % (exc,)) from exc


def resolve_midi_output_port_name():
    """
    Return the name of the MIDI output port to open.

    1. If ``JUST_INTONATION_MIDI_DEVICE_ID`` is set, treat it as a 0-based
       index into ``mido.get_output_names()``.
    2. Otherwise pick the first output whose name contains
       ``JUST_INTONATION_MIDI_OUT_NAME`` (default: ``loopbe``, case-insensitive).
    """
    names = _list_midi_output_names()
    if 'JUST_INTONATION_MIDI_DEVICE_ID' in os.environ:
        device_id = int(os.environ['JUST_INTONATION_MIDI_DEVICE_ID'])
        if device_id < 0 or device_id >= len(names):
            raise RuntimeError(
                'JUST_INTONATION_MIDI_DEVICE_ID=%s is out of range '
                '(there are %s output ports).' % (device_id, len(names)))
        return names[device_id]

    needle = os.environ.get(
        'JUST_INTONATION_MIDI_OUT_NAME', 'loopbe').lower()
    for name in names:
        if needle in name.lower():
            return name

    lines = [
        'No MIDI output port name contains %r.' % needle,
        'Install a virtual MIDI cable (see README.md), then either set',
        'JUST_INTONATION_MIDI_OUT_NAME to a substring of the port name, or',
        'JUST_INTONATION_MIDI_DEVICE_ID to an index from the list below.',
        '',
        'Available MIDI output ports (mido / RtMidi):',
    ]
    if not names:
        lines.append(
            '  (none — install python-rtmidi / ALSA seq as needed; see README.)')
    else:
        for i, name in enumerate(names):
            lines.append('  %s: %s' % (i, name))
    raise RuntimeError('\n'.join(lines))


def _clip_pitchwheel(value):
    return max(mido.MIN_PITCHWHEEL, min(mido.MAX_PITCHWHEEL, int(value)))


rest = 0.5  # seconds


def log2(x):
    return math.log(x, 2)


def freq_to_MIDI(freq):
    A = 440
    return 12 * log2(freq / A) + 69


_midi_port_name = resolve_midi_output_port_name()
midi_port = mido.open_output(_midi_port_name)
atexit.register(midi_port.close)

channels = 16
program = 0


def play_freq(freq, duration=None, sustain=15):
    """
    Use MIDI pitch bends to play arbitrary frequencies.  Bends apply to the
    entire channel, so to support polyphony we cycle through the channels
    for each note, hopefully not letting them collide.

    sustain and duration do the same thing, but one is blocking and the
    other is not?  might not be the right way to do it.
    """
    MIDI_float = freq_to_MIDI(float(freq))
    MIDI_note = int(round(MIDI_float))
    frac = MIDI_float - MIDI_note
    bend_amount = _clip_pitchwheel(frac * 4096)

    channel = play_freq.channel
    play_freq.channel += 1
    play_freq.channel %= channels
    if play_freq.channel == 9:
        """
        Key-based percussion is always on MIDI Channel 10, so skip it.
        """
        play_freq.channel += 1
        play_freq.channel %= channels

    midi_port.send(mido.Message(
        'program_change', channel=channel, program=program))
    midi_port.send(mido.Message(
        'pitchwheel', channel=channel, pitch=bend_amount))
    velocity = random.randint(110, 127)  # Humanize
    midi_port.send(mido.Message(
        'note_on', channel=channel, note=MIDI_note, velocity=velocity))
    if duration is not None:
        time.sleep(duration)
        midi_port.send(mido.Message(
            'note_off', channel=channel, note=MIDI_note, velocity=0))
    else:
        # Prevents synth from choking on all the tails of notes
        # Randomize by 10% so they don't all shut off at once
        rand = random.uniform(0.9, 1.1)

        def _note_off():
            midi_port.send(mido.Message(
                'note_off', channel=channel, note=MIDI_note, velocity=0))

        Timer(sustain * rand, _note_off).start()


play_freq.channel = 0


def play_interval(pitch, interval, rest=0.7):
    """
    Play the interval starting with `pitch`.
    """
    pitch = Pitch(pitch)
    interval = Interval(interval)
    freq_1 = float(pitch)
    freq_2 = float(pitch + interval)
    play_freq(freq_1)
    time.sleep(rest)
    play_freq(freq_2)
    time.sleep(rest)
    play_freq(freq_1)
    play_freq(freq_2)


def play_arp(pitch, intervals, end=True, rest=rest, sustain=2.4):
    """
    Play an arpeggio from root to list of intervals
    interval starting with `pitch`.
    """
    if isinstance(intervals, Chord):
        intervals = intervals.intervals
    root = Pitch(pitch)
    play_freq(root, sustain=sustain)
    time.sleep(rest)
    for interval in intervals:
        play_freq(root + interval, sustain=sustain)
        time.sleep(rest)
    for interval in intervals[-2::-1]:
        play_freq(root + interval, sustain=sustain)
        time.sleep(rest)
    if end:
        play_freq(root, sustain=sustain)


def play_chord(pitch, intervals, sustain=3):
    """
    Play a chord from root to list of intervals
    interval starting with `pitch`.
    """
    print(intervals)
    if isinstance(intervals, Chord):
        intervals = intervals.intervals
    root = Pitch(pitch)
    play_freq(root, sustain=sustain)
    print(root)
    for interval in intervals:
        print(interval)
        play_freq(root + interval, sustain=sustain)


def play_seq(pitch, intervals, rest=rest):
    """
    Play a sequence from root to list of intervals
    interval starting with `pitch`.
    """
    if isinstance(intervals[0], Chord):
        intervals = intervals[0].intervals
    elif all([isinstance(x, Interval) for x in intervals]):
        pass
    elif all([isinstance(x, tuple) for x in intervals]):
        intervals = [Interval(*x) for x in intervals]
    else:
        raise ValueError('sequence not understood')
    root = Pitch(pitch)
    for x in intervals:
        play_freq(root + x)
        time.sleep(rest)


pitch = Pitch(110)

# Lydian mode
lydian = sorted(arange(7) * P5 % P8) + [P8]

# Locrian mode
locrian = sorted(arange(7) * P4 % P8) + [P8]

# play_seq(110, random.sample(locrian, 8))


# Equal:
def equal_major():
    midi_port.send(mido.Message(
        'program_change', channel=0, program=program))
    midi_port.send(mido.Message('pitchwheel', channel=0, pitch=0))
    for note in [57, 61, 64]:
        midi_port.send(mido.Message(
            'note_on', channel=0, note=note, velocity=127))
        Timer(5, lambda n=note: midi_port.send(mido.Message(
            'note_off', channel=0, note=n, velocity=0))).start()
        time.sleep(1)


def just_major():
    play_freq(Pitch(220), sustain=5)
    time.sleep(1)
    play_freq(Pitch(220) + M3, sustain=5)
    time.sleep(1)
    play_freq(Pitch(220) + P5, sustain=5)

#    play_chord(220, Chord(M3, P5))


def equal_minor():
    midi_port.send(mido.Message(
        'program_change', channel=0, program=program))
    midi_port.send(mido.Message('pitchwheel', channel=0, pitch=0))
    for note in [57, 60, 64]:
        midi_port.send(mido.Message(
            'note_on', channel=0, note=note, velocity=127))
        Timer(5, lambda n=note: midi_port.send(mido.Message(
            'note_off', channel=0, note=n, velocity=0))).start()
        time.sleep(1)


def just_minor():
    play_freq(Pitch(220), sustain=5)
    time.sleep(1)
    play_freq(Pitch(220) + m3, sustain=5)
    time.sleep(1)
    play_freq(Pitch(220) + P5, sustain=5)
#    play_chord(220, Chord(m3, P5))
