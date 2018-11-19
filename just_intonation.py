"""
Created on Wed Jul 30 18:55:13 2014

Just intonation classes for music theory experiments in Python
"""

import math
from fractions import Fraction
from numbers import Rational
from itertools import combinations
import math
from functools import reduce

try:
    from math import log2
except ImportError:
    def log2(x):
        return math.log(x, 2)


abbreviations = {
    'P1':  (1, 1),
    'm2':  (16, 15),
    'M2':  (9, 8),  # or 10:9
    'S2':  (8, 7),  # Septimal major second
    'SM2': (8, 7),  # Septimal major second
    's3':  (7, 6),  # Septimal minor third
    'sm3': (7, 6),  # Septimal minor third
    'm3':  (6, 5),  # or 19:16
    'M3':  (5, 4),
    'P4':  (4, 3),
    'P5':  (3, 2),
    'A5':  (25, 16),  # Augmented fifth
    'm6':  (8, 5),    # or 11:7 undecimal minor sixth
    'M6':  (5, 3),    # or 12:7 is septimal major sixth
    'm7':  (16, 9),   # "small just minor seventh"
    # or 9:5 "large just minor seventh"
    'M7':  (15, 8),
    'P8':  (2, 1),
    }


def _lcm(a, b):
    return (a * b) // math.gcd(a, b)


def gcd_rationals(a, b):
    num_gcd = math.gcd(a.numerator, b.numerator)
    denom_lcm = _lcm(a.denominator, b.denominator)
    return Fraction(num_gcd, denom_lcm)


def gcd(*numbers):
    """Return the greatest common divisor of the given integers"""
    return reduce(gcd_rationals, numbers)


def lcm(*numbers):
    """Return lowest common multiple."""
    return reduce(_lcm, numbers, 1)


def gpf(n):
    """
    Find the greatest prime factor of n
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


def is_odd(n):
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
    multiplication, etc.:

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

    References:
    Interval math http://www.moz.ac.at/sem/lehre/lib/bib/software/cm/Notes_from_the_Metalevel/scales.html#sec_15-3-2
    """

    # Use __new__ not __init__ so that these are immutable?
    def __init__(self, numerator, denominator=None):
        """
        Constructs a musical interval
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

        g = gcd(numerator, denominator)
        self._numerator = numerator // g
        self._denominator = denominator // g
        self._terms = self._denominator, self._numerator

    @property
    def numerator(a):
        """
        Numerator of the frequency ratio
        """
        return a._numerator

    @property
    def denominator(a):
        """
        Denominator of the frequency ratio
        """
        return a._denominator

    @property
    def complement(a):
        """
        The musical complement, or inversion, of the interval.
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
            if is_odd(num) and is_odd(den):
                return max(num, den)
            elif is_odd(num):
                den = den // 2
            elif is_odd(den):
                num = num // 2
            else:
                raise Exception('programming mistake: {}:{}'.format(num, den))

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
        # "For a ratio n/d in lowest terms, to find its prime
        # limit, take the product n*d and factor it.  Then report the
        # largest prime you used in the factorization."
        return max(gpf(a._numerator), gpf(a._denominator))

    @property
    def kees_height(a):
        """


        ref: http://xenharmonic.wikispaces.com/Kees+Height
        """
        # "To find its odd limit, simply divide n by 2 until you can no
        # longer divide it without a remainder, then do the same for d.
        # Then report the larger of the two numbers left over."
        # Numerator and denominator are already in reduced form.
        if is_odd(a._numerator) and is_odd(a._denominator):
            return max(a._numerator, a._denominator)
        elif is_odd(a._numerator):
            return a._numerator
        else:
            assert is_odd(a._denominator)
            return a._denominator

    @property
    def benedetti_height(a):
        """
        The measure of inharmonicity used by Giovanni Battista Benedetti,
        which is simply the numerator multiplied by the denominator of the
        frequency ratio in simplest form.

        ref: http://xenharmonic.wikispaces.com/Benedetti+height
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
                raise ValueError('Intervals can only be '
                                 'multiplied by integers')
        except AttributeError:
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
        3*P8 / 3 = P8 (actually c**b = a <-> c = a^(1/b) <-> c = 10**(log10(a)/b))
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
            return False # TODO: or NotImplemented??

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

    def __long__(a):
        """long(a)"""
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
    A musical pitch, an absolute location in logarithmic frequency space

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
        Constructs a musical pitch from a frequency
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
        Frequency of the pitch in hertz
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

    def __long__(a):
        """int(a)"""
        return int(a._frequency)

    def __float__(a):
        """float(a)"""
        return float(a._frequency)


class Chord():
    """
    A combination of notes separated by just intervals

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
    set([Interval(5, 4), Interval(3, 2), Interval(6, 5)])

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
        Constructs a musical chord from a series of intervals relative to
        the root
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
            self._intervals = tuple(Interval(x, root)
                                    for x in terms[1:])

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
            l = lcm(*[x.denominator for x in fractions])
            terms = [l, ]
            terms.extend([x.numerator * l/x.denominator for x in fractions])
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
            l = lcm(*[x.denominator for x in fractions])
            terms = [l, ]
            terms.extend([x.numerator * l/x.denominator for x in fractions])
            assert all(int(x) == x for x in terms)
            terms = [int(x) for x in terms]
            root = terms[0]
            terms = [root] + sorted(set(terms[1:]))
            self._intervals = tuple(Interval(x, root) for x in terms[1:])

        g = gcd(*terms)
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
        List of terms in the frequency ratio that makes up the chord
        """
        return a._terms

    @property
    def intervals(a):
        """
        List of musical intervals that make up the chord, relative to the root
        """
        return a._intervals

    @property
    def steps(a):
        """
        List of musical intervals which, stacked together, produce the chord
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
        The highest prime limit of any interval found in the Chord

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
        Return the nth inversion of a chord.  The first inversion moves the
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
            else:
                # shouldn't be possible, I think
                raise Exception('Programming error')

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
        return (a._terms == b._terms) # TODO: is this ok?  or only public properties?

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


#####################################################




















# TESTS

########################################################


def test_gpf():
    # http://oeis.org/A006530/list
    max_factors = (
        (2, 2), (3, 3), (4, 2), (5, 5), (6, 3), (7, 7), (8, 2), (9, 3),
        (10, 5), (11, 11), (12, 3), (13, 13), (14, 7), (15, 5), (16, 2),
        (17, 17), (18, 3), (19, 19), (20, 5), (21, 7), (22, 11), (23, 23),
        (24, 3), (25, 5), (26, 13), (27, 3), (28, 7), (29, 29), (30, 5),
        (31, 31), (32, 2), (33, 11), (34, 17), (35, 7), (36, 3), (37, 37),
        (38, 19), (39, 13), (40, 5), (41, 41), (42, 7), (43, 43), (44, 11),
        (45, 5), (46, 23), (47, 47), (48, 3), (49, 7), (50, 5), (51, 17),
        (52, 13), (53, 53), (54, 3), (55, 11), (56, 7), (57, 19), (58, 29),
        (59, 59), (60, 5), (61, 61), (62, 31), (63, 7), (64, 2), (65, 13),
        (66, 11), (67, 67), (68, 17), (69, 23), (70, 7), (71, 71), (72, 3),
        (73, 73), (74, 37), (75, 5), (76, 19), (77, 11), (78, 13), (79, 79),
        (80, 5), (81, 3), (82, 41), (83, 83), (84, 7), (85, 17), (86, 43),
        (1000, 5), (1021, 1021),
    )
    for n, m in max_factors:
        assert gpf(n) == m


def test_interval():
    # Construction
    assert Interval(3, 2) == Interval(3, 2)
    assert Interval('P5') == Interval(3, 2)
    assert Interval(Interval('P5')) == Interval(3, 2)
    assert Interval('M3') == Interval(5, 4)
    assert Interval('m3') == Interval(6, 5)
    assert Interval('3:2') == Interval(3, 2)
    assert Interval('4:3') == Interval(4, 3)
    assert Interval('3/2') == Interval(3, 2)

    # Addition and subtraction
    assert Interval(4, 5) + Interval(5, 6) == Interval(2, 3)
    assert M3 + m3 == Interval(3, 2)
    assert -M3 == Interval(4, 5)  # __neg__
    assert +M3 == Interval(5, 4)  # __pos__
    assert abs(Interval(3, 2)) == Interval(3, 2)
    assert abs(Interval(2, 3)) == Interval(3, 2)

    # Shortcut objects
    assert M2 + m2 == m3
    assert M3 + m3 == P5
    assert P4 + M2 == P5
    assert P4 + M3 == M6
    assert P4 + P4 == m7
    assert P4 + P5 == P8
    assert P5 + m2 == m6
    assert P5 + M3 == M7

    # Multiplication and division
    assert P5*12 - P8*7 == Interval(531441, 524288)  # Pythagorean comma
    assert 3*P8 == Interval(8, 1)
    assert P8*4 == Interval(16, 1)
    assert Interval(8) / 3 == P8
    assert Interval(8) / P8 == 3
    assert Interval('P5') * 4 / 4 == Interval('P5')
    assert (Interval(1, 3)*5) / 5 == Interval(1, 3)
    assert (Interval(3, 2)*5) / 5 == Interval(3, 2)

    # Floor division and modulo
    assert Interval(3) // P8 == 1
    assert Interval(4) // P8 == 2
    assert Interval(5) // P8 == 2
    assert Interval(7) // P8 == 2
    assert Interval(8) // P8 == 3
    assert Interval(8) // 3 == Interval(2, 1)
    assert Interval(3) % Interval('P8') == Interval(3, 2)
    assert Interval(5) % Interval('P8') == Interval(5, 4)

    # "The harmonic seventh may be derived from the harmonic series as the
    # interval between the seventh harmonic and the fourth harmonic"
    assert Interval(7) - Interval(4) == Interval(7, 4)

    # Properties
#    assert Interval('6:5').name == 'minor third'

    # http://en.wikipedia.org/wiki/Prime_limit#Examples
    limits = {
        (3, 2): (3, 3),
        (4, 3): (3, 3),
        (5, 4): (5, 5),
        (5, 2): (5, 5),
        (5, 3): (5, 5),
        (7, 5): (7, 7),
        (10, 7): (7, 7),
        (9, 8): (9, 3),
        (27, 16): (27, 3),
        (81, 64): (81, 3),
        (243, 128): (243, 3),
        }
    for interval, (odd_limit, prime_limit) in limits.items():
        assert Interval(*interval).odd_limit == odd_limit
        assert Interval(*interval).prime_limit == prime_limit

    # http://xenharmonic.wikispaces.com/3-limit
    for x in ('128/81', '16/9', '243/128', '256/243', '27/16', '3/2', '32/27',
              '4/3', '81/64', '9/8'):
        assert Interval(x).prime_limit == 3

    # http://xenharmonic.wikispaces.com/5-limit
    for x in ('10/9', '15/8', '16/15', '27/20', '40/27', '5/3', '5/4', '6/5',
              '8/5', '81/80', '9/5'):
        assert Interval(x).prime_limit == 5

    # http://xenharmonic.wikispaces.com/Odd+limit
    for x in ('3/2', '5/4', '7/6', '10/7', '12/7', '9/8', '14/9'):
        assert Interval(x).odd_limit <= 9
    assert Interval('11/9').odd_limit > 9
    assert Interval('15/7').odd_limit > 9

    # http://www.patmissin.com/tunings/tun1.html
    assert Interval('1:1').odd_limit == 1
    assert Interval('1:1').prime_limit == 1

    # http://xenharmonic.wikispaces.com/share/view/69124170
    assert Interval('10:3').odd_limit == 5
    assert Interval(12).odd_limit == 3
    assert Interval(3).odd_limit == 3

    # http://www.tonalsoft.com/enc/l/limit.aspx
    for x in ('81/64', '81/32', '81/16', '81/8', '81/4', '81/2',
              '27/32', '27/16', '27/8', '27/4', '27/2',
              '9/16', '9/8', '9/4', '9/2', '9/1', '18/1', '36/1', '72/1',
              '3/16', '3/8', '3/4', '3/2', '3/1', '6/1', '12/1', '24/1', '48/1',
              '1/16', '1/8', '1/4', '1/2', '1/1', '2/1', '4/1', '8/1', '16/1', '32/1',
              '1/48', '1/24', '1/12', '1/6', '1/3', '2/3', '4/3', '8/3', '16/3', '32/3',
              '1/72', '1/36', '1/18', '1/9', '2/9', '4/9', '8/9', '16/9', '32/9',
              '1/27', '2/27', '4/27', '8/27', '16/27', '32/27', '64/27',
              '1/81', '2/81', '4/81', '8/81', '16/81', '32/81', '64/81', '128/81'):
        assert Interval(x).prime_limit <= 3

    # http://www.tonalsoft.com/enc/l/limit.aspx
    # The 3-limit consists of the following ratios, and all their
    # octave-equivalents:
    for x in ('1/1', '4/3', '3/2'):
        assert Interval(x).odd_limit <= 3
        assert (Interval(x) + 2*P8).odd_limit <= 3
        assert (Interval(x) - P8).odd_limit <= 3

    # The 5-limit consists of the following ratios, and all their
    # octave-equivalents:
    for x in ('1/1', '6/5', '5/4', '4/3', '3/2', '8/5', '5/3'):
        assert Interval(x).odd_limit <= 5
        assert (Interval(x) + 2*P8).odd_limit <= 5
        assert (Interval(x) - P8).odd_limit <= 5

    # The 7-limit consists of the following ratios, and all their
    # octave-equivalents:
    for x in ('1/1', '8/7', '7/6', '6/5', '5/4', '4/3', '7/5', '10/7', '3/2',
              '8/5', '5/3', '12/7', '7/4'):
        assert Interval(x).odd_limit <= 7
        assert (Interval(x) + P8).odd_limit <= 7
        assert (Interval(x) - 3*P8).odd_limit <= 7

    # The 9-limit consists of the following ratios, and all their
    # octave-equivalents:
    for x in ('1/1', '10/9', '9/8', '8/7', '7/6', '6/5', '5/4', '9/7', '4/3',
              '7/5', '10/7', '3/2', '14/9', '8/5', '5/3', '12/7', '7/4',
              '16/9', '9/5'):
        assert Interval(x).odd_limit <= 9
        assert (Interval(x) + P8).odd_limit <= 9
        assert (Interval(x) - 2*P8).odd_limit <= 9

    # The 11-limit consists of the following ratios', 'and all their
    # octave-equivalents:
    for x in ('1/1', '12/11', '11/10', '10/9', '9/8', '8/7', '7/6', '6/5',
              '11/9', '5/4', '14/11', '9/7', '4/3', '11/8', '7/5', '10/7',
              '16/11', '3/2', '14/9', '11/7', '8/5', '18/11', '5/3', '12/7',
              '7/4', '16/9', '9/5', '20/11', '11/6'):
        assert Interval(x).odd_limit <= 11
        assert (Interval(x) + 3*P8).odd_limit <= 11
        assert (Interval(x) - 2*P8).odd_limit <= 11

    # http://xenharmonic.wikispaces.com/Kees+Height
    assert Interval('5/3').kees_height == 5
    assert Interval('4/3').kees_height == 3
    assert Interval('2/1').kees_height == 1

    # http://xenharmonic.wikispaces.com/Kees+Height
    for frac, ben, tenney in (('3/2',     6, 2.585),
                              ('6/5',    30, 4.907),
                              ('9/7',    63, 5.977),
                              ('13/11', 143, 7.160)):
        assert Interval(frac).benedetti_height == ben
        assert round(Interval(frac).tenney_height - tenney, 3) == 0

    # http://xenharmonic.wikispaces.com/Tenney+Height
    for frac, ket, tenney in (('1/1', '|0>',        0           ),
                              ('2/1', '|1>',        1           ),
                              ('3/2', '|-1 1>',     2.5849625007),
                              ('5/4', '|-2 0 1>',   4.3219280948),
                              ('7/4', '|-2 0 0 1>', 4.8073549220),):
        assert round(Interval(frac).tenney_height - tenney, 8) == 0

def test_pitch():
    # Construction
    assert Pitch(100) == Pitch(100)
    assert Pitch(Pitch(100)) == Pitch(100)
    assert Pitch(100) - Interval(3) == Pitch('100/3')
    assert Pitch(100/3).frequency == 100/3

    # Addition and subtraction
    assert Pitch(300) + Interval(3, 2) == Pitch(450)
    assert Pitch(300) - Interval(3, 2) == Pitch(200)
    assert Pitch(300) + -Interval(3, 2) == Pitch(200)
    assert Pitch(300) + Interval(2, 3) == Pitch(200)
    assert Pitch(300) - Pitch(200) == Interval(3, 2)
    assert Pitch(200) - Pitch(300) == Interval(2, 3)
    assert Pitch(550) - Pitch(440) == Interval(5, 4)

    # Properties
    assert Pitch(440).frequency == 440

def test_chord():
    # Construction
    assert Chord(2, 4, 6) == Chord(1, 2, 3)
    assert Chord(4, 5, 6) == Chord(4, 5, 6)
    assert Chord(4, 6, 5) == Chord(4, 5, 6)
    assert Chord(4, 6, 5) == Chord(4, 5, 6)  # Intervals are sorted
    assert Chord(6, 4, 9) == Chord(6, 4, 9)
    assert Chord(4, 6, 5, 6) == Chord(4, 5, 6)  # Duplicate tones removed
    assert Chord(Interval(3, 2)) == Chord(2, 3)
    assert Chord(Interval(5, 4), Interval(3, 2)) == Chord(4, 5, 6)
    assert Chord(Interval(5, 4), Interval(6, 4)) == Chord(4, 5, 6)
    assert Chord(Interval('3:2'), Interval(2)) == Chord(2, 3, 4)
    assert Chord(Interval('M3'), Interval('m3')) == Chord(20, 24, 25)
    assert Chord(M3) == Chord(4, 5)
    assert Chord(M3) == Interval(5, 4)  # Is this ok?
    assert Chord(M3, m3) == Chord(20, 24, 25)
    assert Chord(M3, P5) == Chord(4, 5, 6)
    assert Chord(P5, M3) == Chord(4, 5, 6)
    assert Chord(-P5, +P5) == Chord(6, 4, 9)  # Lowest interval is negative
    assert Chord(+P5, -P5) == Chord(6, 4, 9)
    assert Chord(P5, P5, P5) == Chord(2, 3)
    assert Chord('4:5:6') == Chord(4, 5, 6)
    assert Chord('4:6:5') == Chord(4, 5, 6)  # Sorted
    assert Chord('6:4:9') == Chord(6, 4, 9)
    assert Chord('1 : 2 : 3') == Chord(1, 2, 3)
    assert Chord('1 5/4 3/2 5/3') == Chord(12, 15, 18, 20)
    assert Chord('1-5/4-3/2-5/3') == Chord(12, 15, 18, 20)
    assert Chord('1/1 – 5/4 – 3/2') == Chord(4, 5, 6)
    assert Chord('1:3:5:7:9') == Chord(1, 3, 5, 7, 9)  # otonal
    assert Chord('1/9:1/7:1/5:1/3:1/1') == Chord(35, 45, 63, 105, 315) # utonal
    assert Chord('3/2', '4/3') == Chord(6, 8, 9)
    assert Chord('4/3', '3/2') == Chord(6, 8, 9)
    assert Chord(('3:2'), 2) == Chord(2, 3, 4)
    assert Chord('3 4 5') == Chord(3, 4, 5)  # List of terms, not intervals
    assert Chord('3', '4', '5') == Chord(1, 3, 4, 5)  # List of intervals
    assert Chord((5, 4), (3, 2)) == Chord(4, 5, 6)
    assert Chord((5, 4), (6, 5)) == Chord(20, 24, 25)
    assert Chord((6, 5), (5, 4)) == Chord(20, 24, 25)

#    Chord('major') = Chord(4, 5, 6)?  or better name?

    # Inversion
    assert Chord(4, 5, 6).inversion(1) == Chord(5, 6, 8)
    assert Chord(4, 5, 6).inversion(2) == Chord(3, 4, 5)
    assert Chord(4, 5, 6).inversion(3) == Chord(4, 5, 6)
    assert Chord(4, 5, 6, 7).inversion(1) == Chord(5, 6, 7, 8)
    assert Chord(4, 5, 6, 7).inversion(2) == Chord(6, 7, 8, 10)
    assert Chord(4, 5, 6, 7).inversion(3) == Chord(7, 8, 10, 12)
    assert Chord(4, 5, 6, 7).inversion(4) == Chord(4, 5, 6, 7)
    assert Chord(-P5, +P5).inversion(1) == Chord(P4, P5) == Chord(6, 8, 9)

    # Negation
    assert (-Chord(1, 2, 3)).intervals == (Interval(1, 3), Interval(1, 2))
    assert -Chord(-P8, -P5) == Chord(2, 3, 4)
    assert abs(-Chord(1, 2, 3)) == Chord(1, 2, 3)
    assert abs(Chord(6, 3, 4)) == Chord(2, 3, 4)

    # Properties
    assert Chord(11, 13, 14, 12).terms == (11, 12, 13, 14)
    assert Chord(4, 5, 6).intervals == (Interval(5, 4), Interval(3, 2))
    assert Chord(P5, P5, P5).intervals == (Interval(3, 2),)
    assert Chord(4, 5, 6).steps == (Interval(5, 4), Interval(6, 5))

    # http://www.72note.com/erlich/limit.html
    assert Chord('1/1 5/4 3/2 7/4').prime_limit == 7
    assert Chord('1/1 8/7 21/16 3/2 7/4').prime_limit == 7

    # http://x31eq.com/ass.htm
    assert Chord('3:5:9:15').odd_limit == 9
    assert Chord('3:7:9:21').odd_limit == 9

    # http://www.tallkite.com/misc_files/alt-tuner_manual_and_primer.pdf
    # "A major chord 1/1 – 5/4 – 3/2 has an odd limit of 5, regardless of
    # the voicing."
    assert Chord('1/1 – 5/4 – 3/2').odd_limit == 5
    assert Chord('1/1 – 5/4 – 3/2').inversion(1).odd_limit == 5
    assert Chord('1/1 – 5/4 – 3/2').inversion(2).odd_limit == 5

    assert Chord('1/1 – 5/4 – 3/2 – 15/8').odd_limit == 15  # maj7 chord
    assert Chord('1/1 – 6/5 – 16/25').odd_limit == 25       # dim triad
    assert Chord('1/1 – 5/4 – 3/2 – 9/5').odd_limit == 25   # dom7 chord
    assert Chord('1/1 – 5/4 – 3/2 – 7/4').odd_limit == 7    # dom7 chord
    assert Chord('1/1 – 6/5 – 7/5').odd_limit == 7          # dim chord

    # http://strasheela.sourceforge.net/strasheela/doc/Example-MicrotonalChordProgression.html
    assert Chord('1/1, 5/4, 3/2').prime_limit == 5
    assert Chord('1/4, 8/5, 4/3').prime_limit == 5
    assert Chord('1/1, 5/4, 3/2, 7/4').prime_limit == 7
    assert Chord('1/1, 8/5, 4/3, 8/7').prime_limit == 7
    assert Chord('1/1, 9/8, 5/4, 11/8, 3/2, 7/4').prime_limit == 11
    assert Chord('1/1, 16/9, 8/5, 16/11, 4/3, 8/7').prime_limit == 11


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    # TODO: this is screwing up IPython's _

    import pytest
    pytest.main(['--tb=short', __file__])

#    import nose
#    result = nose.run()

    pass
