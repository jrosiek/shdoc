
from collections import deque
from collections import namedtuple
import re

COMMENT = re.compile(r"^\s*#\s*")
FUNC_DECL = re.compile(r"(?P<func>function\s+)?(?P<name>[-a-zA-Z0-9_:.]+)(?(func)(\(\))?|\(\)).*")
DIRECTIVE = re.compile(r"@(?P<name>[a-zA-Z0-9_]+)\s*")

ContentType = namedtuple("ContentType", "name pattern")

Loc = namedtuple("Loc", "line column")
Token = namedtuple("Token", "type data content_type loc")

WORD_CONTENT = ContentType("word", re.compile(r"\S+\s*"))
TEXT_CONTENT = ContentType("text", re.compile(r".*$"))

class Lexer(object):
    def __init__(self, stream, name):
        self.stream = stream
        self.name = name
        self.tokens = deque()
        self.current_line = None
        self.line_index = 0
        self.line_pos = 0
        self.loc = Loc(0, 0)
        self.indent = [0]

    def peek(self, content_type):
        if self.tokens:
            token = self.tokens[0]
            if token.content_type is not None and token.content_type != content_type:
                assert token.loc.line == self.line_index
                self.line_pos = token.loc.column
                self._advance(0)    # update self.loc
                self.tokens.clear() # Remove buffered tokens
        if not self.tokens:
            self._make_more(content_type)
        assert self.tokens
        return self.tokens[0]


    def lex(self, content_type):
        result = self.peek(content_type)
        self.tokens.popleft()
        return result


    def _push(self, name, data, content_type=None):
        self.tokens.append(Token(name, data, content_type, self.loc))

    
    def _advance(self, l):
        self.line_pos += l
        self.loc = Loc(self.line_index, self.line_pos)
    

    def _advance_line(self):
        self.line_index += 1
        self.line_pos = 0
        self._advance(0)


    def _push_match(self, name, match, content_type=None):
        self._push(name, match, content_type)
        self._advance(len(match.group(0)))


    def _push_invalid(self, msg):
        self._push('invalid', 
                  '%s:%d:%d: %s' % (self.name, self.line_index, self.line_pos+1, msg))


    def _make_more(self, content_type):
        if not self.current_line or self.line_pos >= len(self.current_line):
            self._next_line()
            assert self.tokens
            return 

        m = self._match_more(content_type.pattern)
        if not m:
            return self._push_invalid('invalid syntax, expected <%s>' % content_type.name)

        self._push_match(content_type.name, m, content_type)

    
    def _strip_nl(self, text):
        if text.endswith("\n"):
            return text[:-1]
        return text


    def _next_line(self):
        while not self.tokens:
            self.current_line = self.stream.readline()
            if not self.current_line:
                self.tokens.append(None)
                continue
            self.current_line = self._strip_nl(self.current_line)
            self._advance_line()
            #print(repr(self.current_line))

            # Preprocess line
            m = COMMENT.match(self.current_line)
            if m:
                # Comment
                l = len(m.group(0))
                #print ">>>", repr(m.group(0))
                if l < len(self.current_line):
                    self._process_indent(l)
                    self._advance(l)
                    self._process_comment()
                else:
                    # Empty comment line
                    self._advance(l)
            else:
                text = self.current_line.lstrip()
                l = len(self.current_line) - len(text)
                self._process_indent(l)
                self._advance(l)
                self._process_code()


    def _process_indent(self, n):
        assert n >= 0
        while n < self.indent[-1]:
            self.indent.pop()
            self._push('dedent', self.indent[-1])

        if n > self.indent[-1]:
            self.indent.append(n)
            self._push('indent', n)


    def _match_more(self, pattern):
        #print "@>", repr(self.current_line[self.line_pos:])
        return pattern.match(self.current_line, self.line_pos)


    def _process_code(self):
        m = self._match_more(FUNC_DECL)
        if m:
            return self._push_match('func-decl', m)

        self._push('code', self.current_line)
        self._advance(len(self.current_line))


    def _process_comment(self):
        m = self._match_more(DIRECTIVE)
        if m:
            return self._push_match(m.group("name"), m)



        


if __name__ == "__main__":
    text="""\
  ddsadasd
    ala::ma() {
#
# @module module name here
# 
# Here is a place for some documentation. 
# @module directive starts documentation of a file.
#
# Empty line starts a new paragraph
# 
# @authors Author Name <author.name@domain.com>
#
# Documentation can be interspersed by directives. It will be
#     joined together in the final documentation.
#  Unnecesary and inconsistent indentation is allowed
# 
# Empty lines are not required between text and directives.
# @author
#   Another Author <another.author@domain.com>
#   
#   Different Author <different.author@domain.com>
#
# Directives @author and @authors are aliases. All authors will be merged together.
# If authors are on a new line, they must be indented. Each author can span only single line.

#
# @func This is short description: this function does this
#   and that (continuation is indented)
# This is part of long documentation because is not indented. sentence 1.
# Sentence 2
#
# A new documentation paragraph here.
#
# @arg name type description
# 
# @args
#   name type this is a very
#       long description
#
#   name2 type2 description2
#
# Similarly to @author/@authors, directives @arg, @args are aliases. 
# Their content will be merged together.
#
# @exitcode 5 description
#
# @exitcodes
#   0 description
#   >0 failure
#
# Directive @exitcode/@exitcodes behaves similarily to @arg/@args
#
# @stdin What is expected on stdin
# @stdout What will be on stdout
#
#   Here is even another paragraph
# @stderr What will be on stderr
#
# Directives @std* can be provided only once for given function
#
# @see other::function
#
# @see
#   a_different_function
#   and_one::more
#
function some::name {
}

# @func Function defined without 'function' keyword
other::function() 
{
}

# More notes:
# 1. Directive is allowed only at the beginning of a comment line and must be unindented.
"""
    import StringIO
    data = StringIO.StringIO(text)

    l = Lexer(data, "a_file")
    tok = l.peek(TEXT_CONTENT)
    while tok is not None:
        print(tok)
        if tok.type == "text":
            tok = l.lex(WORD_CONTENT)
            print "#>", tok
        else:
            l.lex(TEXT_CONTENT)

        tok = l.peek(TEXT_CONTENT)


#    print(l._next_line())


