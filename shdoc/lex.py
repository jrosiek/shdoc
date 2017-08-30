
from collections import deque

from .lines import *
from .patterns import *


START_OF_LINE = PatternSequence([
    ("-empty-comment-line", r"^(?P<indent>\s*#+[^\S\n]*)$\n?"),
    ("-comment-line",       r"^(?P<indent>\s*#+[^\S\n]*)"),
    ("-code-line",          r"^(?P<indent>\s*)(?=\S)"),
    ("-skip",               r"^(?P<indent>[^\S\n]*)$\n?"),
])

CODE_LINE = PatternSequence([
    ("-func",           r"(?P<func>function\s+)?(?P<name>[-a-zA-Z0-9_:.]+)(?(func)(\(\))?|\(\)).*$\n?"),
    ("-code",           r".*$\n?")
])

COMMENT_LINE = PatternSequence([
    ("-token",          r"\S+[^\S\n]*"), # TODO: accept quoted token
    ("-eol",            r"$\n?"),
])

COMMENT_LINE_START = PatternSequence([
    ("-directive",      r"@(?P<name>[a-zA-Z0-9_]+)[^\S\n]*"),
]).then(COMMENT_LINE)



class Token(object):
    def __init__(self, name, match=None, value=None):
        self.name = name
        self.match = match
        self.value = value

    def __repr__(self):
        return "Token({}:{})".format(
            self.name, 
            self.value if self.value else self.match)


class Lexer(object):
    def __init__(self, stream):
        self._loc = Loc.start_of(Line.from_stream(stream))
        self._tokens = deque()
        self._indent = [0]
        self._state = self._state_start_of_line

    def peek(self):
        try:
            old_loc = object()
            while not self._tokens and old_loc != self._loc:
                old_loc = self._loc
                self._state()
            return self._tokens[0]
        except:
            print("error: {}".format(self._loc))
            raise

    def take(self):
        self.peek() # produce if there are no tokens
        return self._tokens.popleft()

    def _push(self, token):
        self._tokens.append(token)

    def _match(self, pattern_seq):
        m = pattern_seq.match(self._loc)
        self._loc = m.loc_after
        return m

    def _update_indent(self, newIndent):
        while newIndent < self._indent[-1]:
            self._push(Token('dedent', value=self._indent[-1]))
            self._indent.pop()
        if newIndent > self._indent[-1]:
            self._push(Token("indent", value=newIndent))
            self._indent.append(newIndent)

    def _state_start_of_line(self):
        if self._loc is None:
            return self._push(Token("eof"))

        m = self._match(START_OF_LINE)

        if m.name == "-empty-comment-line":
            self._push(Token("eol", match=m))
        else:
    #        print(repr(m.group("indent")))
            self._update_indent(len(m.group("indent")))
            if m.name == "-comment-line":
                self._state = self._state_comment_line_start
            elif m.name == "-code-line":
                self._state = self._state_code_line
            elif m.name == "-skip":
                pass
            else:
                assert False

    def _state_code_line(self):
        m = self._match(CODE_LINE)
        self._state = self._state_start_of_line

        if m.name == "-func":
            return self._push(Token("func", match=m, value=m.group("name")))
        # Ignore other lines

    def _state_comment_line_start(self):
        m = self._match(COMMENT_LINE_START)
        self._comment_line_match(m)
    
    def _state_comment_line(self):
        m = self._match(COMMENT_LINE)
        self._comment_line_match(m)

    def _comment_line_match(self, m):
        if m.name == "-eol":
            self._push(Token("eol", match=m))
            self._state = self._state_start_of_line
        else:
            self._state = self._state_comment_line
            if m.name == "-directive":
                self._push(Token("directive-" + m.group("name"), match=m, value=m.group("name")))
            elif m.name == "-token":
                self._push(Token("token", match=m, value=m.group(0)))
            else:
                assert False
            

    

if __name__ == "__main__":
    import six
    s = Stream(six.StringIO("""\

function alama::kota {

}

# @func asdasdasa and go @there
#   sdsa
#       
# fdsfs
xyz()\
"""))

    l = Lexer(s)
    t = l.take()
    i = 0
    while t.name != 'eof':
        print(t)
        t = l.take()
        i += 1
        if i > 100:
            print("too many")
            break
    else:
        print(t)
