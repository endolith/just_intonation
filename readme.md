Probably all of this is redundant with [Scala](http://www.huygens-fokker.org/scala/), but

1. I don't know how to use it
2. I wanted to learn by doing:
   - Just Intonation
   - object-oriented Python
   - unit testing

Maybe odd-limit and prime-limit should be objects rather than properties?
"The limit" is a set of intervals, and includes all intervals of `<=` a certain
height, so `.height` should be the property name and `OddLimit` should be a class?

Examples:

* https://soundcloud.com/endolith/everything-is-a-power-chord-in-just-intonation
* https://soundcloud.com/endolith/enumerating-the-rationals

This module provides:

* `Interval(numerator, denominator)`
  * `.numerator`
  * `.denominator`
  * `.complement`
  * `.odd_limit`
  * `.prime_limit`
  * `.kees_height`
  * `.benedetti_height`
  * `.tenney_height`
* `Pitch(frequency)`
  * `.frequency`
* `Chord(4, 5, 6)`, `Chord(Interval('M3'), Interval('P5'))`, etc.
  * `.terms`
  * `.intervals`
  * `.steps`
  * `.all_steps`
  * `.odd_limit`
  * `.prime_limit`
  * `.inversion()`
* Convenience intervals `P1`, `m2`, `M2`, `m3`, `M3`, `P4`, `P5`, etc.



