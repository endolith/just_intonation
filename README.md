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

## Examples

* [Everything is a power chord in just intonation](https://soundcloud.com/endolith/everything-is-a-power-chord-in-just-intonation) - Dyads made from the harmonic series, first in piano, then undistorted guitar, then distorted guitar.
* [Enumerating the rationals](https://soundcloud.com/endolith/enumerating-the-rationals) - A small portion of the Calkin-Wilf sequence, played on a fractal piano with an infinite number of keys.
