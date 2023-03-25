"""
Classes for Just intonation music theory experiments in Python.
"""

# Created on Wed Jul 30 18:55:13 2014

import math
from math import log2
from fractions import Fraction
from numbers import Rational
from itertools import combinations
from functools import reduce


abbreviations = {
    'P1':  (1, 1),
    'm2':  (16, 15),
    # 10:9 = M2^5 in FJS
    'M2':  (9, 8),

    # https://en.wikipedia.org/wiki/Septimal_whole_tone
    'S2':  (8, 7),  # Septimal major second
    'SM2': (8, 7),  # Septimal major second

    # https://en.wikipedia.org/wiki/Septimal_minor_third
    's3':  (7, 6),  # Septimal minor third
    'sm3': (7, 6),  # Septimal minor third

    # 19:16 = m3^{19} in FJS
    'm3':  (6, 5),
    'M3':  (5, 4),
    'P4':  (4, 3),
    'P5':  (3, 2),

    # https://www.huygens-fokker.org/docs/intervals.html
    'A5':  (25, 16),  # Classic augmented fifth (not in FJS?)

    'm6':  (8, 5),
    'M6':  (5, 3),
    # 12:7 is septimal major sixth = M6_7 in FJS

    # https://en.xen.wiki/w/16/9 FJS name is m7
    'm7':  (16, 9),   # "small just minor seventh"

    # 9:5 "large just minor seventh" = m7_5 in FJS
    'M7':  (15, 8),
    'P8':  (2, 1),
    }


def _lcm_pairwise(a, b):
    return (a * b) // math.gcd(a, b)


def _gcd_rationals(a, b):
    num_gcd = math.gcd(a.numerator, b.numerator)
    denom_lcm = _lcm_pairwise(a.denominator, b.denominator)
    return Fraction(num_gcd, denom_lcm)


def _gcd(*numbers):
    """Return the greatest common divisor of the given integers."""
    return reduce(_gcd_rationals, numbers)


def _lcm(*numbers):
    """Return lowest common multiple."""
    return reduce(_lcm_pairwise, numbers, 1)


def _gpf(n):
    """
    Find the greatest prime factor of n.
    """
    if n < 1:
        raise ValueError('{} does not have a prime factorization'.format(n))
    if n == 1:
        # Technically the answer is None, but 1 is accepted in music theory?
        return 1
    divisor = 2
    while n > 1:
        if not n % divisor:
            n /= divisor
            divisor -= 1
        divisor += 1
    return divisor


def _F(a):
    return Fraction(a.numerator, a.denominator)


def _is_odd(n):
    return bool(n % 2)


class Interval(object):
    """
    A just intonation (JI) musical interval; the distance spanned by a dyad.

    There are several ways to construct intervals.  For instance, the perfect
    fifth:

    >>> Interval(3, 2)
    Interval(3, 2)
    >>> Interval('3:2')
    Interval(3, 2)
    >>> Interval('3/2')
    Interval(3, 2)

    Some abbreviations are also understood:

    >>> Interval('P5')
    Interval(3, 2)

    Intervals are relative distances between pitches on a musical scale (in
    logarithmic frequency space).  Mathematical operations are handled
    accordingly, so multiplication becomes addition, powers become
    multiplication, etc.:[1]_ [2]_

    >>> Fraction(5, 4) * Fraction(6, 5)
    Fraction(3, 2)
    >>> Interval(5, 4) + Interval(6, 5)
    Interval(3, 2)
    >>> Interval(3, 2) - Interval(6, 5)
    Interval(5, 4)

    So a span of 3 octaves is:

    >>> 3 * Interval(2, 1)
    Interval(8, 1)

    Other operations are supported where they make sense, such as octave
    reduction of the 5th harmonic, which is found in the 2nd octave:

    >>> Interval(5) % Interval('P8')
    Interval(5, 4)
    >>> Interval(5) // Interval('P8')
    2

    or the 8th harmonic being 3 octaves above the root

    >>> Interval(8) / Interval('P8')
    3
    >>> Interval(8) / 3
    Interval(2, 1)

    Complement (musical inversion):

    >>> Interval('P8') - Interval(3, 2)
    Interval(4, 3)
    >>> Interval('P8') - Interval(6, 5)
    Interval(5, 3)

    Negation (ratio inversion): An interval with a smaller first term is
    considered to be below the root note instead of above it:

    >>> -Interval(3, 2)
    Interval(2, 3)

    Comparisons:

    >>> max(Interval(256, 243), Interval(9, 8))
    Interval(9, 8)
    >>> Interval(2, 3) < Interval(3, 2)
    True
    >>> abs(Interval(2, 3)) == Interval(3, 2)
    True

    Intervals have some properties:

    >>> Interval('P5').complement
    Interval(4, 3)
    >>> Interval(9, 8).odd_limit
    9
    >>> Interval(9, 8).prime_limit
    3

    The module also has shortcut variables for the common intervals. For
    instance, the Pythagorean comma can be calculated as:

    >>> P5 * 12 - P8 * 7
    Interval(531441, 524288)

    References
    ----------
    .. [1] Heinrich Konrad Taube, "Notes from the Metalevel", Chapter 15
       "Microtonality, Tunings and Modes", section "Interval Math".
       https://web.archive.org/web/20151014145657/http://www.moz.ac.at/sem/lehre/lib/bib/software/cm/Notes_from_the_Metalevel/scales.html#sec_15-3-2
    .. [2] misotanni, "The FJS Crash Course", Lesson 0: Preliminary
       https://misotanni.github.io/fjs/en/crash.html#lesson-0
    """

    # Use __new__ not __init__ so that these are immutable?
    def __init__(self, numerator, denominator=None):
        """
        Construct a musical interval.
        """
        if numerator == 0:
            raise ValueError('No such thing as 0 interval')

        if denominator is None:
            if isinstance(numerator, Interval):
                """
                >>> Interval(Interval(3, 2))
                Interval(3, 2)
                """
                interval = numerator
                self._numerator = interval.numerator
                self._denominator = interval.denominator
                return

            elif isinstance(numerator, Rational):
                """
                >>> Interval(Fraction(3, 2))
                Interval(3, 2)

                >>> Interval(3)
                Interval(3, 1)
                """
                rational = numerator
                self._numerator = rational.numerator
                self._denominator = rational.denominator
                return

            elif isinstance(numerator, str):
                """
                Construction from strings

                >>> Interval('3:2')
                Interval(3, 2)

                >>> Interval('3/2')
                Interval(3, 2)

                >>> Interval('3')
                Interval(3, 1)
                """
                input_string = numerator
                try:
                    numerator, denominator = abbreviations[input_string]
                except KeyError:
                    input_string = input_string.replace(':', '/')
                    try:
                        frac = Fraction(input_string)
                    except ValueError:
                        raise ValueError('Invalid literal for Interval: %r' %
                                         numerator)
                    numerator = frac.numerator
                    denominator = frac.denominator

            else:
                raise TypeError("argument should be a string "
                                "or a Rational instance")

        """
        Construction from numerator and denominator

        >>> Interval(3, 2)
        Interval(3, 2)

        >>> Interval(6, 4)
        Interval(3, 2)
        """

        g = _gcd(numerator, denominator)
        self._numerator = numerator // g
        self._denominator = denominator // g
        self._terms = self._denominator, self._numerator

    @property
    def numerator(a):
        """
        Numerator of the frequency ratio.
        """
        return a._numerator

    @property
    def denominator(a):
        """
        Denominator of the frequency ratio.
        """
        return a._denominator

    @property
    def complement(a):
        """
        Return the musical complement, or inversion, of the interval.

        When summed, an interval and its complement produce an octave.
        """
        return P8 - a

    @property
    def odd_limit(a):
        """
        The lowest odd-limit the interval is in; the greatest odd number found
        in the frequency ratio (after powers of 2 are removed).  For instance,
        the "7 odd-limit" includes 7:6 and 6:5, but not 9:7 or 15:14.

        (If this returns 5, then the interval is in the 5 and 7 odd-limits,
        but not in the 3 odd-limit.)

        "generally preferred for the analysis of simultaneous intervals and
        chords"
        """
        # "To find its odd limit, simply divide n by 2 until you can no
        # longer divide it without a remainder, then do the same for d.
        # Then report the larger of the two numbers left over."
        # Numerator and denominator are already in reduced form.
        num = a._numerator
        den = a._denominator
        while True:
            if _is_odd(num) and _is_odd(den):
                return max(num, den)
            elif _is_odd(num):
                den = den // 2
            elif _is_odd(den):
                num = num // 2
            else:  # pragma: no cover
                raise Exception('Programming mistake: {}:{}'.format(num, den))

    @property
    def prime_limit(a):
        """
        The prime-limit of the interval; the greatest prime factor of the
        numbers in the interval's frequency ratio.  For instance, the
        "7-limit" includes 7:6 and 6:5, as well as 9:7 and 15:14.

        Generally used for analysis of scales, since intervals with
        large integers may still have low odd-limit relationships to other
        notes in the scale even if they are high odd-limit relative to the
        root.
        """
        # https://en.xen.wiki/w/2-limit includes unisons (special case)
        if a._numerator == a._denominator == 1:
            return 2

        # "For a ratio n/d in lowest terms, to find its prime
        # limit, take the product n*d and factor it.  Then report the
        # largest prime you used in the factorization."
        return max(_gpf(a._numerator), _gpf(a._denominator))

    @property
    def kees_height(a):
        """
        "The set of JI intervals with Kees semi-height less than or equal to an
        odd integer q comprises the q odd limit."

        ref: https://en.xen.wiki/w/Kees_semi-height
        """
        # "To find its odd limit, simply divide n by 2 until you can no
        # longer divide it without a remainder, then do the same for d.
        # Then report the larger of the two numbers left over."
        # Numerator and denominator are already in reduced form.
        if _is_odd(a._numerator) and _is_odd(a._denominator):
            return max(a._numerator, a._denominator)
        elif _is_odd(a._numerator):
            return a._numerator
        else:
            assert _is_odd(a._denominator)
            return a._denominator

    @property
    def weil_height(a):
        """
        "If p/q is a positive rational number reduced to its lowest terms, then
        the [multiplicative] Weil height is the integer max(p,q)."

        ref: https://en.xen.wiki/w/Weil_height
        """
        return max(a._numerator, a._denominator)

    @property
    def benedetti_height(a):
        """
        The measure of inharmonicity used by Giovanni Battista Benedetti,
        which is simply the numerator multiplied by the denominator of the
        frequency ratio in simplest form.

        ref: https://en.xen.wiki/w/Benedetti_height
        """
        return a._numerator * a._denominator

    @property
    def tenney_height(a):
        """
        The "harmonic distance" function used by James Tenney, also called
        "Tenney norm".

        ref: http://www.plainsound.org/pdfs/JC&ToH.pdf
        """
        return log2(a._numerator * a._denominator)

    def __repr__(self):
        """
        >>> repr(Interval(3, 2))
        'Interval(3, 2)'
        """
        return '%s(%s, %s)' % (self.__class__.__name__,
                               self._numerator, self._denominator)

    def __str__(self):
        """
        >>> str(Interval(3, 2))
        '3:2'
        """
        return '%s:%s' % (self._numerator, self._denominator)

    def __add__(a, b):
        """
        >>> Interval('P4') + Interval('P5')
        Interval(2, 1)
        """
        if isinstance(b, Interval):
            return Interval(_F(a) * _F(b))

    def __sub__(a, b):
        """
        >>> Interval('P8') - Interval('P4')
        Interval(3, 2)
        """
        if isinstance(b, Interval):
            return Interval(_F(a) / _F(b))

    def __mul__(a, b):
        """
        >>> Interval(2, 1) * 3
        Interval(8, 1)

        Multiplying by non-integers would produce non-Intervals(always?),
        and so is not allowed.
        """
        try:
            if int(b) == b:
                return Interval(_F(a) ** int(b))
            else:
                raise TypeError
        except (TypeError, AttributeError):
            raise TypeError('Intervals can only be multiplied by integers')

    __rmul__ = __mul__
    """
    >>> 3 * Interval(2, 1)
    Interval(8, 1)
    """

    def __div__(a, b):
        """
        a / b

        Valid:
        3*P8 / 3 = P8 (actually c**b = a <-> c =
                       a^(1/b) <-> c = 10**(log10(a)/b))
        3*P8 / P8 = 3 (actually b**c = a <-> c = log(a, base=b))

        Invalid:
        8 / P8 = ??

        """
        if isinstance(b, Interval):
            """
            >>> Interval(8) / Interval(2)
            3
            """
            result = math.log(_F(a), _F(b))
            result_int = int(round(result))
            # Convert to exact int result if possible
            if _F(b)**result_int == _F(a):
                return result_int
            else:
                return result

        elif int(b) == b:
            """
            >>> Interval(8) / 3
            Interval(2, 1)
            """
            b = int(b)
            num = a.numerator
            den = a.denominator
            num_result = int(round(10**(math.log10(num) / b)))
            den_result = int(round(10**(math.log10(den) / b)))

            if num_result**b == num and den_result**b == den:
                return Interval(num_result, den_result)
            else:
                raise ValueError('{} cannot be '
                                 'divided exactly by {}'.format(a, b))

        else:
            return NotImplemented

    __truediv__ = __div__

    def __floordiv__(a, b):
        if isinstance(b, Interval):
            """
            >>> Interval(3) // Interval(2)
            1
            """
            result = math.log(_F(a), _F(b))
            result_int = int(result)
            return result_int

        elif int(b) == b:
            """
            >>> Interval(8) // 3
            Interval(2, 1)
            """
            # Basically doesn't make sense?  But does if division does?
            return a / b
        else:
            return NotImplemented

    def __mod__(a, b):
        """
        Octave equivalence, for instance:

        >>> Interval(3) % Interval(2)
        Interval(3, 2)

        >>> Interval(5) % Interval(2)
        Interval(5, 4)
        """
        div = a // b
        return a - b * div

    def __pos__(a):
        """
        >>> +Interval(3, 2)
        Interval(3, 2)
        """
        return a

    def __neg__(a):
        """
        >>> -Interval(3, 2)
        Interval(2, 3)
        """
        return Interval(a.denominator, a.numerator)

    def __abs__(a):
        """
        >>> abs(Interval(2, 3))
        Interval(3, 2)
        """
        if a < Interval(1, 1):
            return -a
        else:
            return a

    def __eq__(a, b):
        """a == b"""
        if isinstance(b, Interval):
            return (a._numerator == b.numerator and
                    a._denominator == b.denominator)
        else:
            return False  # TODO: or NotImplemented??

    def __lt__(a, b):
        """a < b"""
        return _F(a) < _F(b)

    def __gt__(a, b):
        """a > b"""
        return _F(a) > _F(b)

    def __le__(a, b):
        """a <= b"""
        return _F(a) <= _F(b)

    def __ge__(a, b):
        """a >= b"""
        return _F(a) >= _F(b)

    def __bool__(a):
        """a != 0"""
        return True

    def __int__(a):
        """int(a)"""
        return int(a._numerator / a._denominator)

    def __float__(a):
        """float(a)"""
        return float(a._numerator / a._denominator)

    def __hash__(self):
        """hash(self)"""
        # Does not mean that
        return hash(_F(self))


class Pitch(object):
    """
    A musical pitch, an absolute location in logarithmic frequency space.

    Can be summed with intervals to produce other pitches, etc.

    Pitches and math on Intervals is defined in logarithmic space.  So you
    cannot do ``Pitch(440) * 2``.  You have to do:

    >>> Pitch(440) + Interval(2)
    Pitch(880)

    This may seem like a strange way to do things until you think about it
    like this:

    >>> A440 = Pitch(440)    # 440 Hz 'concert A'
    >>> P8 = Interval(2, 1)  # up an octave
    >>> A880 = Pitch(880)
    >>> A440 + P8 == A880
    True

    This is consistent with the way math is done on musical scales.

    >>> M3 + m3 == P5
    True

    Pitches try to have exact Fraction frequency if possible:

    >>> Pitch(100) + Interval('M2')
    Pitch('225/2')
    >>> Pitch(100*9/8)
    Pitch(112.5)

    The distance between two pitches is an interval:

    >>> Pitch(440) - Pitch(330)
    Interval(4, 3)
    >>> Pitch(440) - Interval(4, 3)
    Pitch(330)
    """

    def __init__(self, frequency):
        """
        Construct a musical pitch from a frequency.
        """
        if isinstance(frequency, Pitch):
            self._frequency = frequency.frequency
        elif isinstance(frequency, Fraction):
            self._frequency = frequency
        elif isinstance(frequency, float):
            self._frequency = frequency
        else:
            self._frequency = Fraction(frequency)

        if int(self._frequency) == self._frequency:
            self._frequency = int(frequency)

        if self._frequency < 0:
            raise ValueError('Pitch frequency cannot be negative')

    @property
    def frequency(a):
        """
        Frequency of the pitch in hertz.
        """
        return a._frequency

    def __repr__(self):
        """repr(self)"""
        if isinstance(self._frequency, Fraction):
            return ("%s('%s')" % (self.__class__.__name__, self._frequency))
        else:
            # int(self._frequency) == self._frequency:
            return ("%s(%s)" % (self.__class__.__name__, self._frequency))

    def __str__(self):
        """str(self)"""
        return '%s Hz' % float(self._frequency)

    def __add__(a, b):
        """
        >>> Pitch(440) + Interval(5, 4)
        Pitch(550)
        """
        if isinstance(b, Interval):
            return Pitch(a._frequency * _F(b))
        else:
            return NotImplemented

    def __sub__(a, b):
        if isinstance(b, Interval):
            """
            >>> Pitch(440) - Interval(4, 3)
            Pitch(330)
            """
            return Pitch(a._frequency / _F(b))
        elif isinstance(b, Pitch):
            """
            >>> Pitch(440) - Pitch(330)
            Interval(4, 3)
            """
            return Interval(_F(a._frequency) / _F(b.frequency))
        else:
            return NotImplemented

    def __lt__(a, b):
        """a < b"""
        return a._frequency < b.frequency

    def __gt__(a, b):
        """a > b"""
        return a._frequency > b.frequency

    def __le__(a, b):
        """a <= b"""
        return a._frequency <= b.frequency

    def __ge__(a, b):
        """a >= b"""
        return a._frequency >= b.frequency

    def __bool__(a):
        """a != 0"""
        return a._frequency != 0

    def __neg__(a):
        """-a"""
        raise ValueError('Pitch cannot be negative')

    def __eq__(a, b):
        """a == b"""
        return (a._frequency == b.frequency)

    def __int__(a):
        """int(a)"""
        return int(a._frequency)

    def __float__(a):
        """float(a)"""
        return float(a._frequency)


class Chord():
    """
    A combination of notes separated by just intervals.

    Chords can be constructed several ways.  For instance, the major chord can
    be constructed from a list of (possibly fractional) frequency ratio terms:

    >>> Chord(4, 5, 6)
    Chord(4, 5, 6)
    >>> Chord('4:5:6')
    Chord(4, 5, 6)
    >>> Chord('1-5/4-3/2')
    Chord(4, 5, 6)
    >>> Chord('1/1 – 5/4 – 3/2')
    Chord(4, 5, 6)

    or a list of intervals relative to the root:

    >>> Chord(Interval('M3'), Interval('P5'))
    Chord(4, 5, 6)
    >>> Chord('5/4', '3/2')
    Chord(4, 5, 6)
    >>> Chord((5, 4), (3, 2))
    Chord(4, 5, 6)

    Beware the difference:

    >>> Chord('4 5 6')
    Chord(4, 5, 6)
    >>> Chord(Interval(4), Interval(5), Interval(6))
    Chord(1, 4, 5, 6)

    Intervals are relative to a root, not stacked:

    >>> Chord(M3, m3)
    Chord(20, 24, 25)

    Intervals are sorted and duplicate tones removed:

    >>> Chord(4, 6, 5, 6)
    Chord(4, 5, 6)

    But this does not necessarily mean that the *terms* are sorted.  Intervals
    can be negative from the root, which produces terms that decrease.  (Chords
    are not assumed to be in "root position" or "normal form"):

    >>> Chord(-P5, -M3)
    Chord(15, 10, 12)
    >>> Chord(-P5, P5)
    Chord(6, 4, 9)

    Note that the order of terms is backwards for Chords vs Intervals:

    >>> Chord(Interval(3, 2))
    Chord(2, 3)
    >>> Chord(Interval(5, 4), Interval(6, 4))
    Chord(4, 5, 6)

    (This is potentially confusing, but is the way they are typically
    represented.  It may be changed in the future.)

    The terms, intervals from root, and intermediate stacked steps of the
    Chord can be accessed:

    >>> Chord(M3, P5).terms
    (4, 5, 6)
    >>> Chord(4, 5, 6).intervals
    (Interval(5, 4), Interval(3, 2))
    >>> Chord(4, 5, 6).steps
    (Interval(5, 4), Interval(6, 5))
    >>> Chord(4, 5, 6).all_steps
    {Interval(5, 4), Interval(6, 5), Interval(3, 2)}

    as well as the limits:

    >>> Chord(20, 25, 30, 36).odd_limit
    25
    >>> Chord(20, 25, 30, 36).prime_limit
    5

    Musical inversion moves the lowest tone an octave higher:

    >>> Chord(4, 5, 6).inversion(1)
    Chord(5, 6, 8)
    >>> Chord(4, 5, 6).inversion(2)
    Chord(3, 4, 5)

    Negating a chord makes all the intervals negative relative to the root
    (converting it from the otonal overtone series to the utonal undertone
    series):

    >>> -Chord(1, 2, 3)
    Chord(6, 2, 3)
    >>> Chord('1/1 1/2 1/3')
    Chord(6, 2, 3)

    NOT accepted: (0, 4, 7) equal temperament notation for major chord.  (The
    4th note of what scale?)
    """

    def __init__(self, *args):
        """
        Construct a musical chord from a series of intervals relative to
        the root.
        """
        if len(args) == 1 and isinstance(args[0], str):
            """
            Handle construction from a single string of (possibly fractional)
            terms:
            Chord('4:5:6') == Chord(4, 5, 6)
            Chord('1/1 – 5/4 – 3/2') == Chord(4, 5, 6)
            Chord('1-5/4-3/2-5/3') == Chord(12, 15, 18, 20)
            Chord('1 5/4 3/2 5/3') == Chord(12, 15, 18, 20)
            Chord('1/1, 5/4, 3/2, 7/4') == Chord(4, 5, 6, 7)

            but
            Chord('3 4 5') == Chord('3:4:5') == Chord(3, 4, 5)??
            or
            Chord('3 4 5') == Chord(Interval(3), Interval(4), Interval(5)) ==
                              Chord(1, 3, 4, 5)??

            and what about
            Chord('4:5 2:3') == Chord(4, 5, 6)?
            """
            args = args[0]
            if ':' in args:
                sep = ':'
            elif ',' in args:
                sep = ','
            elif '–' in args:
                sep = '–'
            elif '-' in args:
                sep = '-'
            elif ' ' in args:
                sep = ' '
            else:
                raise ValueError('String argument "{}" not '
                                 'understood'.format(args))

            terms = [Fraction(x) for x in args.split(sep)]
            root = terms[0]
            terms = [root] + sorted(set(terms[1:]))
            self._intervals = tuple(Interval(x, root) for x in terms[1:])

        elif all([isinstance(x, Interval) for x in args]):
            """
            List of Interval objects:

            >>> Chord(M3, P5)
            Chord(4, 5, 6)
            >>> Chord(Interval(3, 2))
            Chord(2, 3)
            >>> Chord(Interval(5, 4), Interval(3, 2))
            Chord(4, 5, 6)
            >>> Chord(Interval('3:2'), Interval(2))
            Chord(2, 3, 4)
            """
            self._intervals = tuple(sorted(set(args)))
            fractions = sorted([_F(x) for x in set(args)])
            lcm = _lcm(*[x.denominator for x in fractions])
            terms = [lcm, ]
            terms.extend([x.numerator * lcm/x.denominator for x in fractions])
            assert all(int(x) == x for x in terms)
            terms = [int(x) for x in terms]
        elif all([isinstance(x, int) for x in args]):
            """
            List of terms:

            >>> Chord(4, 5, 6)
            Chord(4, 5, 6)
            >>> Chord(2, 4, 6)  # Converted to reduced form
            Chord(1, 2, 3)
            >>> Chord(4, 6, 5)  # Intervals are sorted
            Chord(4, 5, 6)
            >>> Chord(6, 4, 9)  #  First interval is negative
            Chord(4, 5, 6)
            """
            terms = list(args)
            root = terms[0]
            terms = [root] + sorted(set(terms[1:]))
            self._intervals = tuple(Interval(x, root) for x in terms[1:])
        else:
            """
            List of Interval arguments:

            >>> Chord((5, 4), (3, 2))
            Chord(4, 5, 6)
            >>> Chord('3:2', 2)
            Chord(2, 3, 4)
            """
            try:
                fractions = sorted([_F(Interval(*x)) for x in args])
            except TypeError:
                try:
                    fractions = sorted([_F(Interval(x)) for x in args])
                except TypeError:
                    raise ValueError('Chord construction args "{}" '
                                     'not understood'.format(args))
            lcm = _lcm(*[x.denominator for x in fractions])
            terms = [lcm, ]
            terms.extend([x.numerator * lcm/x.denominator for x in fractions])
            assert all(int(x) == x for x in terms)
            terms = [int(x) for x in terms]
            root = terms[0]
            terms = [root] + sorted(set(terms[1:]))
            self._intervals = tuple(Interval(x, root) for x in terms[1:])

        g = _gcd(*terms)
        self._terms = tuple(n // g for n in terms)
        self._steps = tuple([self._intervals[0]] +
                            [j-i for i, j in
                            zip(self._intervals[:-1], self._intervals[1:])])

        ints = [Interval(1)] + list(self.intervals)
        self._all_steps = set([b - a for a, b in list(combinations(ints, 2))])
        assert set(self._intervals) <= self._all_steps
        assert set(self._steps) <= self._all_steps

    @property
    def terms(a):
        """
        List of terms in the frequency ratio that makes up the chord.
        """
        return a._terms

    @property
    def intervals(a):
        """
        List of musical intervals that make up the chord, relative to the root.
        """
        return a._intervals

    @property
    def steps(a):
        """
        List of musical intervals which, stacked together, produce the chord.
        """
        return a._steps

    @property
    def all_steps(a):
        """
        Set of all music intervals that can be made by any tone in the chord
        with any other tone
        """
        return a._all_steps

    @property
    def odd_limit(a):
        """
        The highest odd limit of any interval found in the Chord.

        So the "dyadic odd-limit"? or intervallic

        For example:

        >>> Chord('1/1 – 5/4 – 3/2 – 9/5').odd_limit
        25

        even though

        >>> Chord('1/1 – 5/4 – 3/2 – 9/5').intervals
        (Interval(5, 4), Interval(3, 2), Interval(9, 5))
        >>> Chord('1/1 – 5/4 – 3/2 – 9/5').steps
        (Interval(5, 4), Interval(6, 5), Interval(6, 5))

        because

        >>> Interval('9/5') - Interval('5/4')
        Interval(36, 25)
        """
        # "To find the prime limit or odd limit of a list of ratios (such as
        # a scale), simply calculate it for each of them individually and
        # report the maximum.
        #
        # To find the prime or odd limit of a chord, first compute its
        # table of dyads, e.g. for major triad C-E-G the dyads are C-E,
        # E-G, and C-G.  Then apply the procedure for a list of ratios
        # given above."
        return max(x.odd_limit for x in a._all_steps)

    @property
    def prime_limit(a):
        """
        The highest prime limit of any interval found in the Chord.

        "intervallic limit"

        'Whether Partch used the word "limit" to refer to odd or prime numbers
        is a matter of some debate.'

        'Odd-limit" is generally considered to be the more important when the
        context is a consideration of concordance, whereas "prime-limit" is
        generally the reference in most other cases.'
        """
        return max(x.prime_limit for x in a._all_steps)

    def inversion(self, n):
        """
        Return the nth inversion of a chord.

        The first inversion moves the
        root an octave up and uses the next term as the root.  The second
        inversion moves that tone up an octave, etc.
        """
        x = self
        for step in range(n):
            terms = list(x._terms)
            if terms[0] < terms[1]:
                terms = terms + [terms.pop(0)*2]  # I'm surprised this works
            elif terms[1] < terms[0]:
                terms = terms + [terms.pop(1)*2]  # I'm surprised this works
            else:  # pragma: no cover
                # shouldn't be possible, I think
                raise Exception('Programming mistake')

            root = terms[0]
            terms = [root] + sorted(set(terms[1:]))
            x = Chord(*terms)
        return x

    def __repr__(self):
        """repr(self)"""
        return (self.__class__.__name__ + '(' +
                ', '.join((str(n) for n in self._terms)) + ')')

    def __str__(self):
        """str(self)"""
        return ':'.join((str(n) for n in self._terms))

    def __eq__(a, b):
        """
        >>> Chord(4, 6, 8) == Chord(2, 3, 4)
        True
        """
        # TODO: is this ok?  or only public properties?
        return (a._terms == b._terms)

    def __neg__(a):
        """
        >>> -Chord(1, 2, 3)
        Chord(6, 2, 3)
        """
        return Chord(*(-x for x in a.intervals[::-1]))

    def __abs__(a):
        """
        >>> abs(Chord(6, 3, 4))
        Chord(2, 3, 4)
        """
        return Chord(*sorted(abs(x) for x in a.intervals))


# Convenience shortcuts
P1 = Interval('P1')
m2 = Interval('m2')
M2 = Interval('M2')
m3 = Interval('m3')
M3 = Interval('M3')
P4 = Interval('P4')
P5 = Interval('P5')
m6 = Interval('m6')
M6 = Interval('M6')
m7 = Interval('m7')
M7 = Interval('M7')
P8 = Interval('P8')
