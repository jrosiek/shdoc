
import re

DIRECTIVE = re.compile(r"^#(?P<space>\s+)@(?P<name>\w+)\s+") 
EMPTY_COMMENT = re.compile(r"^#(?P<space>\s*)$")
COMMENT = re.compile(r"^#(?P<space>\s+)")
CODE = re.compile(r".*")

class Token(object):
    def __init__(self, type, text=None):
        self.type = type
        self.text = text

    def __repr__(self):
        if self.text is not None:
          return "%s[%s]" % (self.type, self.text)
        return "%s" % self.type


class Lexer(object):
    def __init__(self, stream):
        self.stream = stream
        self.current_line = None
        self.remaining = ""
        self.indent = []

    def _categorize_line(self):
        m = DIRECTIVE.match(self.current_line)
        if m:
            if len(m.group("space")) != 1:
                return m, Token("invalid", "directive cannot be indented")
            return m, Token('directive-' + m.group("name"))
        m = EMPTY_COMMENT.match(self.current_line)
        if m:
            return m, Token("nl")
        m = COMMENT.match(self.current_line)

        
        return CODE.match(self.current_line), Token('code')

    def _next_line(self):
        self.current_line = self.stream.readline()
        if not self.current_line:
            return Token('eof')

        m, token = self._categorize_line()
        self.remaining = self.current_line[len(m.group(0)):]
        return token

    def _lex(self, content_pattern, content_symbol):
        if not remaining:
            result = self._next_line()

        


if __name__ == "__main__":
    text="""
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
    l = Lexer(data)

    print(l._next_line())

