"""
Created on Tue Aug 26 22:27:10 2014

So to play MIDI chords, put each note on its
own channel, pitch bend them by less than one semitone to correct the pitch
and then play them all at once
"""

import time
from fractions import Fraction
from threading import Timer  # :D

# modded for pitch bend: https://github.com/pygame/pygame/pull/394
from pygame import midi

import random
import math
from numpy import arange
from numpy.random import randint
from just_intonation import (Interval, Pitch, Chord, P1, m2, M2, m3, M3,
                             P4, P5, m6, M6, m7, M7, P8)

rest = 0.5  # seconds

def log2(x):
    return math.log(x, 2)

def freq_to_MIDI(freq):
    A = 440
    return 12 * log2(freq / A) + 69

midi.init()

if 'LoopBe' in midi.get_device_info(3)[1]:
    try:
        synth = midi.Output(3)
    except Exception as e:
        if 'Invalid device ID' in str(e):
            synth.close()
            synth = midi.Output(3)
        else:
            raise
else:
    raise Exception('Loopback MIDI device not found')

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
        Timer(sustain*rand, synth.note_off, (MIDI_note, 0, channel)).start()

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
lydian = sorted(arange(7)*P5 % P8) + [P8]

# Locrian mode
locrian = sorted(arange(7)*P4 % P8) + [P8]

# play_seq(110, random.sample(locrian, 8))


# Equal:
def equal_major():
    synth.set_instrument(program, channel=0)
    synth.pitch_bend(channel=0)
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
    synth.pitch_bend(channel=0)
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
