
import six

from shdoc.lines import *
from shdoc.patterns import *


def test_pattern_can_match_to_correct_data(capsys):
    source = six.StringIO("""\
abcdefgh
wxyz""")
    s = Stream(source)
    l = Line.from_stream(s)
    
    loc = Loc.start_of(l).advance(2)

    p = Pattern(r"(cde).*$\n?")

    m = p.match(loc)

    assert m.loc == loc
    assert m.loc_after == Loc.start_of(l.next)

    assert m.group(1) == "cde"
    assert m.pattern == p


def test_pattern_hash_and_equality_depend_on_regex():
    a = Pattern("a")
    b = Pattern("a")
    c = Pattern("b")

    assert hash(a) == hash(b)
    assert a == b
    assert hash(a) != hash(c)
    assert a != c


def test_start_of_a_line_matches_only_start_of_a_line():
    source = six.StringIO("""\
aaaa""")

    
    s = Stream(source)
    l = Line.from_stream(s)
    
    loc = Loc.start_of(l)

    p = Pattern(r"^aa")

    assert p.match(loc) is not None
    assert p.match(loc.advance(1)) is None



def test_pattern_sequence_matches_first_pattern(capsys):
    x = [
            ("p1", r"d.f"),
            ("p1", r"abc"),
            ("p2", r"a.cd"),
        ]

    seq = PatternSequence(x[:2]).then(x[2:])

    source = six.StringIO("""\
abcdefaxcdz""")

    s = Stream(source)
    l = Line.from_stream(s)
    
    loc = Loc.start_of(l)

    m = seq.match(loc)
    assert m.name == "p1"
    assert m.loc_after == loc.advance(3)
    assert m.group(0) == "abc"
    assert m.pattern_seq == PatternSequence(x[:2])
    
    m = seq.match(loc.advance(1))
    assert m is None

    m = seq.match(loc.advance(3))
    assert m.name == "p1"
    assert m.loc_after == loc.advance(6)
    assert m.group(0) == "def"
    assert m.pattern_seq == PatternSequence(x[:1])

    m = seq.match(loc.advance(6))
    assert m.name == "p2"
    assert m.loc_after == loc.advance(10)
    assert m.group(0) == "axcd"
    assert m.pattern_seq == seq



def test_pattern_sequence_hash_and_equality_depends_on_definition():
    a = PatternSequence([("a", "x")]).then("b", "y")
    b = PatternSequence([("a", "x"), ("b", "y")])

    c = PatternSequence([("b", "y")]).then("a", "x")
    d = PatternSequence([("Z", "x"), ("b", "y")])
    e = PatternSequence([("a", "Z"), ("b", "y")])

    assert hash(a) == hash(b)
    assert a == b
    
    assert hash(a) != hash(c)
    assert a != c
    assert hash(a) != hash(d)
    assert a != d
    assert hash(a) != hash(e)
    assert a != e


def test_pattern_sequence_is_prefix_behaves_correctly():
    x = [
            ("p1", r"d.f"),
            ("p1", r"abc"),
            ("p2", r"a.cd"),
        ]

    seq = PatternSequence(x[:2]).then(x[2:])

    assert seq.is_prefix(seq)
    assert PatternSequence(x[:2]).is_prefix(seq)
    assert not seq.is_prefix(PatternSequence(x[:2]))
    assert PatternSequence(x[:1]).is_prefix(seq)
    assert not seq.is_prefix(PatternSequence(x[:1]))
    assert PatternSequence([]).is_prefix(seq)
    assert not seq.is_prefix(PatternSequence([]))

    assert not PatternSequence(x[:2]).is_prefix(PatternSequence(x[1:]))
    assert not PatternSequence(x[1:]).is_prefix(PatternSequence(x[:2]))
    

