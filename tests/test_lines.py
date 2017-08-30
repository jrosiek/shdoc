
import six

from shdoc.lines import *


def test_lines_can_be_used_to_read_file():
    stream = six.StringIO("""\
Concurrently with this course, students take physics and a second
semester of calculus, as well as a second semester
in the humanities.""")

    l = Line.from_stream(Stream(stream, "memory"))
    assert l.text == "Concurrently with this course, students take physics and a second\n"
    assert l.row_index == 0

    l = l.next
    assert l.text == "semester of calculus, as well as a second semester\n"
    assert l.row_index == 1

    assert l.next == l.next

    l = l.next
    assert l.text == "in the humanities."
    assert l.row_index == 2

    assert l.next is None


def test_loc_can_advance_over_multiple_lines():
    stream = six.StringIO("""\
Concurrently with
this course,
stu
dents""")

    l = Loc.start_of(Line.from_stream(Stream(stream, "memory")))

    assert l.text_at == "Concurrently with\n"

    assert l.advance(11) == l.advance(11)

    l = l.advance(10)
    assert l.text_at == "ly with\n"


    l = l.advance(7)
    assert l.text_at == "\n"

    l = l.advance(2)
    assert l.text_at == "his course,\n"


    l = l.advance(16)
    assert l.text_at == "dents"

    assert l.advance(100) is None

