# -*- coding: utf-8 -*-
"""
Play just-intonation material over MIDI using pitch bend.

Each note uses its own MIDI channel so polyphony can stay in tune: the
script picks the nearest MIDI note number and applies a small pitch-bend
offset for the remaining cents.

This module expects a *virtual MIDI cable* (or similar) as the PortMidi /
pygame output device. You send MIDI from this script into the cable, and a
separate synthesizer program listens on the other end of the cable.

See the "MIDI playback" section in README.md for setup (LoopBe, loopMIDI,
Linux ALSA routing, environment variables).
"""

from __future__ import division, print_function

import os
import time
import random
import math
from threading import Timer

# modded for pitch bend: https://github.com/endolith/pygame/blob/master/lib/midi.py
from pygame import midi
from numpy import arange

from just_intonation import Interval, Pitch, Chord, m3, M3, P4, P5, P8


def _midi_device_name(device_info):
    """Return a Unicode device name; pygame may give bytes on some platforms."""
    name = device_info[1]
    if isinstance(name, bytes):
        return name.decode('utf-8', errors='replace')
    return str(name)


def _list_midi_output_devices():
    """Yield (device_id, name) for each PortMidi output device."""
    for device_id in range(midi.get_count()):
        info = midi.get_device_info(device_id)
        if info is None:
            continue
        _interf, _name, is_input, is_output, _opened = info
        if is_output:
            yield device_id, _midi_device_name(info)


def resolve_midi_output_device_id():
    """
    Pick the pygame / PortMidi output device used by this script.

    Resolution order:

    1. If the environment variable ``JUST_INTONATION_MIDI_DEVICE_ID`` is set
       to an integer, use that device id (must be an output device).
    2. Otherwise scan outputs whose name contains the substring from
       ``JUST_INTONATION_MIDI_OUT_NAME`` (default: ``loopbe``, case-insensitive).
       This matches Windows *LoopBe1* ports ("LoopBe Internal MIDI", etc.).
    """
    if 'JUST_INTONATION_MIDI_DEVICE_ID' in os.environ:
        device_id = int(os.environ['JUST_INTONATION_MIDI_DEVICE_ID'])
        info = midi.get_device_info(device_id)
        if info is None:
            raise RuntimeError(
                'JUST_INTONATION_MIDI_DEVICE_ID=%s is out of range '
                '(midi.get_count() == %s).' % (device_id, midi.get_count()))
        if not info[3]:
            raise RuntimeError(
                'JUST_INTONATION_MIDI_DEVICE_ID=%s is not a MIDI output.' % (
                    device_id,))
        return device_id

    needle = os.environ.get(
        'JUST_INTONATION_MIDI_OUT_NAME', 'loopbe').lower()
    outputs = list(_list_midi_output_devices())
    for device_id, name in outputs:
        if needle in name.lower():
            return device_id

    lines = ['No MIDI output device name contains %r.' % needle,
             'Install a virtual MIDI cable (see README.md), then either',
             '  set JUST_INTONATION_MIDI_OUT_NAME to a unique substring of',
             '  its port name, or set JUST_INTONATION_MIDI_DEVICE_ID to a',
             '  number from the list below.',
             '',
             'Available MIDI *output* devices:']
    if not outputs:
        lines.append('  (none — PortMidi sees no writable outputs; on Linux'
                      ' check ALSA `seq` / `snd_seq` and that pygame was built'
                      ' with MIDI support.)')
    else:
        for device_id, name in outputs:
            lines.append('  %s: %s' % (device_id, name))
    raise RuntimeError('\n'.join(lines))


rest = 0.5  # seconds


def log2(x):
    return math.log(x, 2)


def freq_to_MIDI(freq):
    A = 440
    return 12 * log2(freq / A) + 69


midi.init()

_output_id = resolve_midi_output_device_id()
try:
    synth = midi.Output(_output_id)
except Exception:
    midi.quit()
    raise

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
    bend_amount = int(frac * 4096)

    channel = play_freq.channel
    play_freq.channel += 1
    play_freq.channel %= channels
    if play_freq.channel == 9:
        """
        Key-based percussion is always on MIDI Channel 10, so skip it.
        """
        play_freq.channel += 1
        play_freq.channel %= channels

    synth.set_instrument(program, channel)
    synth.pitch_bend(bend_amount, channel)
    velocity = random.randint(110, 127)  # Humanize
    synth.note_on(MIDI_note, velocity, channel)
    if duration is not None:
        time.sleep(duration)
        synth.note_off(MIDI_note, 0, channel)
    else:
        # Prevents synth from choking on all the tails of notes
        # Randomize by 10% so they don't all shut off at once
        rand = random.uniform(0.9, 1.1)
        Timer(sustain * rand, synth.note_off, (MIDI_note, 0, channel)).start()


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
    synth.set_instrument(program, channel=0)
    synth.pitch_bend(0, channel=0)
    for note in [57, 61, 64]:
        synth.note_on(note, 127, 0)
        Timer(5, synth.note_off, (note, 0, 0)).start()
        time.sleep(1)
#    synth.set_instrument(program,channel=1)
#    synth.pitch_bend(channel=1)
#    for note in [57, 61, 64]:
#        synth.note_on(note, 127, 0)
#        Timer(5, synth.note_off, (note, 0, 0)).start()


def just_major():
    play_freq(Pitch(220), sustain=5)
    time.sleep(1)
    play_freq(Pitch(220) + M3, sustain=5)
    time.sleep(1)
    play_freq(Pitch(220) + P5, sustain=5)

#    play_chord(220, Chord(M3, P5))


def equal_minor():
    synth.set_instrument(program, channel=0)
    synth.pitch_bend(0, channel=0)
    for note in [57, 60, 64]:
        synth.note_on(note, 127, 0)
        Timer(5, synth.note_off, (note, 0, 0)).start()
        time.sleep(1)


def just_minor():
    play_freq(Pitch(220), sustain=5)
    time.sleep(1)
    play_freq(Pitch(220) + m3, sustain=5)
    time.sleep(1)
    play_freq(Pitch(220) + P5, sustain=5)
#    play_chord(220, Chord(m3, P5))
