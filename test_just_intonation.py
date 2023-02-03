import pytest
from just_intonation import Interval, Pitch, Chord
from just_intonation import P1, m2, M2, m3, M3, P4, P5, m6, M6, m7, M7, P8
from just_intonation import gpf


def test_gpf():
    # http://oeis.org/A006530/list
    max_factors = (
        (1, 1),
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

    with pytest.raises(ValueError):
        gpf(-1)


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
    assert Interval(8) / Interval(3) == pytest.approx(1.892789260714372)
    assert Interval('P5') * 4 / 4 == Interval('P5')
    assert (Interval(1, 3)*5) / 5 == Interval(1, 3)
    assert (Interval(3, 2)*5) / 5 == Interval(3, 2)

    with pytest.raises(ValueError, match='can only be multiplied by integers'):
        P5 * P8

    with pytest.raises(ValueError, match='cannot be divided exactly'):
        P8 / 12

    with pytest.raises(TypeError, match='unsupported operand type'):
        P8 / 3.14

    # Floor division and modulo
    assert Interval(3) // P8 == 1
    assert Interval(4) // P8 == 2
    assert Interval(5) // P8 == 2
    assert Interval(7) // P8 == 2
    assert Interval(8) // P8 == 3
    assert Interval(8) // 3 == Interval(2, 1)
    assert Interval(3) % Interval('P8') == Interval(3, 2)
    assert Interval(5) % Interval('P8') == Interval(5, 4)

    with pytest.raises(TypeError, match='unsupported operand type'):
        P8 // 3.14

    # Inequalities
    assert P8 > m3
    assert P8 >= M2
    assert P4 < P5
    assert M3 <= m6
    assert bool(P1)

    # "The harmonic seventh may be derived from the harmonic series as the
    # interval between the seventh harmonic and the fourth harmonic"
    assert Interval(7) - Interval(4) == Interval(7, 4)

    # Properties
#    assert Interval('6:5').name == 'minor third'

    limits = {
        # https://en.xen.wiki/w/2-limit [prime limit]
        # "unisons, octaves and stacks of octaves"
        # https://en.xen.wiki/w/1-odd-limit
        # "only the unison (and all it's octavations)."
        (1, 1): (1, 2),
        (2, 1): (1, 2),
        (4, 1): (1, 2),

        # http://en.wikipedia.org/wiki/Prime_limit#Examples
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

    # https://en.xen.wiki/w/3-limit
    for x in ('128/81', '16/9', '243/128', '256/243', '27/16', '3/2', '32/27',
              '4/3', '81/64', '9/8', '2187/2048', '8192/6561', '1024/729'):
        assert Interval(x).prime_limit == 3

    # https://en.xen.wiki/w/5-limit
    for x in ('10/9', '15/8', '16/15', '27/20', '40/27', '5/3', '5/4', '6/5',
              '8/5', '81/80', '9/5', '135/128', '1215/1024', '256/135'):
        assert Interval(x).prime_limit == 5

    # https://en.xen.wiki/w/Odd_limit
    for x in ('3/2', '5/4', '7/6', '10/7', '12/7', '9/8', '14/9'):
        assert Interval(x).odd_limit <= 9
    assert Interval('11/9').odd_limit > 9
    assert Interval('15/7').odd_limit > 9

    # http://www.patmissin.com/tunings/tun1.html
    assert Interval('1:1').odd_limit == 1
    # assert Interval('1:1').prime_limit == 1  # Contradicts below link

    # http://www.tonalsoft.com/enc/l/limit.aspx#MainContent
    assert Interval('1:4').prime_limit == 2
    assert Interval('1:2').prime_limit == 2
    assert Interval('1:1').prime_limit == 2
    assert Interval('2:1').prime_limit == 2
    assert Interval('4:1').prime_limit == 2

    # http://xenharmonic.wikispaces.com/share/view/69124170 [???]
    assert Interval('10:3').odd_limit == 5
    assert Interval(12).odd_limit == 3
    assert Interval(3).odd_limit == 3

    # http://www.tonalsoft.com/enc/l/limit.aspx
    # Representation of 2-dimensional infinite set
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

    # https://en.xen.wiki/w/Kees_semi-height
    assert Interval('7/4').kees_height == 7
    assert Interval('7/5').kees_height == 7
    assert Interval('7/6').kees_height == 7
    assert Interval('8/7').kees_height == 7
    assert Interval('5/3').kees_height == 5
    assert Interval('8/5').kees_height == 5
    assert Interval('5/4').kees_height == 5
    assert Interval('6/5').kees_height == 5
    assert Interval('4/3').kees_height == 3
    assert Interval('3/2').kees_height == 3
    assert Interval('2/1').kees_height == 1
    assert Interval('9/5').kees_height == 9
    assert Interval('10/9').kees_height == 9
    assert Interval('15/14').kees_height == 15
    assert Interval('28/15').kees_height == 15
    assert Interval('25/26').kees_height == 25
    assert Interval('27/25').kees_height == 27
    assert Interval('25/24').kees_height == 25

    # https://en.xen.wiki/w/Benedetti_height
    for frac, ben, tenney in (('1/1',     1, 0),
                              ('2/1',     2, 1),
                              ('3/2',     6, 2.585),
                              ('6/5',    30, 4.907),
                              ('9/7',    63, 5.977),
                              ('13/11', 143, 7.160)):
        assert Interval(frac).benedetti_height == ben
        assert round(Interval(frac).tenney_height - tenney, 3) == 0

    # https://en.xen.wiki/w/Tenney_height
    for frac, ket, tenney in (('1/1', '|0>',        0           ),
                              ('2/1', '|1>',        1           ),
                              ('3/2', '|-1 1>',     2.5849625007),
                              ('5/4', '|-2 0 1>',   4.3219280948),
                              ('7/4', '|-2 0 0 1>', 4.8073549220),):
        assert round(Interval(frac).tenney_height - tenney, 8) == 0

    # https://en.wikipedia.org/wiki/Complement_(music)
    assert Interval('M3').complement == Interval('m6')
    assert Interval('P1').complement == Interval('P8')
    assert Interval('P4').complement == Interval('P5')

    # https://en.xen.wiki/w/Octave_complement
    assert Interval('m3').complement == Interval('M6')

    # String representation
    assert str(Interval(5, 4)) == '5:4'
    assert str(Interval(7)) == '7:1'
    assert str(P5*12 - P8*7) == '531441:524288'

    # Numerical representation
    assert int(Interval(7)) == 7
    assert float(Interval(3, 2)) == pytest.approx(1.5)

    # Invalid inputs
    with pytest.raises(ValueError, match='No such thing'):
        Interval(0)

    with pytest.raises(ValueError, match='Invalid literal'):
        Interval('spam')

    with pytest.raises(TypeError, match='should be a string or a Rational'):
        Interval([1, 2])


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

    # Inequalities
    assert Pitch(440) > Pitch(220)
    assert Pitch(440) >= Pitch(220)
    assert Pitch(100) < Pitch(200)
    assert Pitch(1000) <= Pitch(1000)
    assert bool(Pitch(150))

    # String representation
    assert str(Pitch(440)) == '440.0 Hz'

    # Numerical representation
    assert float(Pitch(100)) == 100

    # Invalid input
    with pytest.raises(ValueError, match='cannot be negative'):
        Pitch(-440)

    with pytest.raises(ValueError, match='cannot be negative'):
        -Pitch(440)

    with pytest.raises(TypeError, match='unsupported operand type'):
        Pitch(440) + 440

    with pytest.raises(TypeError, match='unsupported operand type'):
        Pitch(440) - 440


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

    assert Chord(4, 5, 6).all_steps == {M3, m3, P5}

    # String representation
    assert str(Chord(4, 5, 6)) == '4:5:6'

    # Invalid input
    with pytest.raises(ValueError, match='not understood'):
        Chord('major')

    with pytest.raises(ValueError, match='not understood'):
        Chord([4, 5, 6])


if __name__ == "__main__":
    # Test doctests
    import doctest
    doctest.testmod()
    # TODO: this is screwing up IPython's _

    # Test assertions
    import pytest
    pytest.main(['--tb=short', __file__])
