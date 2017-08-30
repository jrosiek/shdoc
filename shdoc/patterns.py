
import re
import wrapt

from . import lines


class Pattern(object):
    def __init__(self, pattern):
        self._re = re.compile(pattern)

    def __repr__(self):
        return "Pattern({})".format(repr(self._re.pattern))

    def match(self, loc):
        m = self._re.match(loc.line.text, loc.column_index)
        if not m:
            return None
        return Match(m, loc, self)

    def __hash__(self):
        return hash(self._re.pattern)

    def __eq__(self, other):
        return isinstance(other, Pattern) \
            and self._re.pattern == other._re.pattern



class Match(wrapt.ObjectProxy):
    def __init__(self, m, loc, pattern):
        super(Match, self).__init__(m)
        self._self_loc = loc
        self._self_pattern = pattern
        self._self_name = None
        self._self_pattern_seq = None

    @property
    def loc(self):
        return self._self_loc

    @property
    def pattern(self):
        return self._self_pattern

    @property
    def name(self):
        return self._self_name

    @name.setter
    def name(self, value):
        self._self_name = value

    @property
    def pattern_seq(self):
        return self._self_pattern_seq
   
    @pattern_seq.setter
    def pattern_seq(self, value):
        self._self_pattern_seq = value

    @property
    def loc_after(self):
        return self._self_loc.advance(len(self.__wrapped__.group(0)))

    def __repr__(self):
        return "Match({}:{})".format(self._self_loc, repr(self.__wrapped__.group(0)))

    def __str__(self):
        return repr(self)



class PatternSequence(object):
    def __init__(self, data):
        l = []
        for name, pat in data:
            if not isinstance(pat, Pattern):
                pat = Pattern(pat)
            l.append((name, pat))
        self._data = tuple(l)

    def match(self, loc):
        for i, (name, pat) in enumerate(self._data):
            m = pat.match(loc)
            if m is not None:
                m.name = name
                m.pattern_seq = PatternSequence(self._data[:(i+1)])
                return m
        return None

    def then(self, a, b=None):
        if b is None:
            if isinstance(a, PatternSequence):
                return PatternSequence(self._data + a._data)
            else:
                return self.then(PatternSequence(a))
        return self.then(PatternSequence([(a, b)]))

    def is_prefix(self, other):
        l = len(self._data)
        return l <= len(other._data) and \
            other._data[:l] == self._data

    def __repr__(self):
        return "PatternSequence({})".format(self._data)

    def __hash__(self):
        return hash(self._data)

    def __eq__(self, other):
        return isinstance(other, PatternSequence) \
            and self._data == other._data





