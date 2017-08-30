

class Stream(object):
    """Named text source"""
    def __init__(self, source, name="<unnamed>"):
        self.source = source
        self.name = name

    def __repr__(self):
        return "Stream({})".format(self.name)



class Line(object):
    """Line of text that knows its index and what lines follow it"""
    def __init__(self, stream, text, row_index):
        assert isinstance(stream, Stream)
        self._stream = stream
        self._text = text
        self._row_index = row_index
        self._has_next = False
        self._next = None

    @property
    def stream(self): return self._stream

    @property
    def row_index(self): return self._row_index

    @property
    def text(self): return self._text

    @staticmethod
    def from_stream(stream, row_index = 0):
        text = stream.source.readline()
        if not text:
            return None
        return Line(stream, text, row_index)

    @property
    def next(self):
        if not self._has_next:
            self._next = Line.from_stream(self._stream, self._row_index + 1)
            self._has_next = True
        return self._next

    def __repr__(self):
        return "Line({}:{})".format(self._row_index, repr(self._text))



class Loc(object):
    """Text location that can be advanced to succeeding locations"""
    def __init__(self, line, column_index = 0):
        self._line = line
        self._column_index = column_index

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self._line == other._line and self._column_index == other._column_index

    @staticmethod
    def start_of(line):
        if line is None:
            return None
        return Loc(line)

    @property
    def line(self): return self._line

    @property
    def column_index(self): return self._column_index

    @property
    def text_at(self):
        return self._line.text[self._column_index:]

    def advance(self, n):
        new_column_index = self._column_index + n
        line_len = len(self._line._text)
        if new_column_index < line_len:
            return Loc(self._line, new_column_index)
        else:
            new_line_loc = Loc.start_of(self._line.next)
            if new_line_loc is None:
                return None
            return new_line_loc.advance(n - line_len + self._column_index)

    def __repr__(self):
        return "Loc({}:{}:{}:{})".format(
            self._line.stream.name, 
            self._line.row_index + 1, 
            self._column_index + 1,
            repr(self._line.text[self._column_index:]))





