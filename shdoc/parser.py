
from .lex import *

class Parser(object):
    def __init__(self, stream):
        self._lex = Lexer(stream)
        self._error_count = 0

    def parse(self):
        return self._file()

    def _file(self):
        result = self._block()
        self._lex.take()
        pass

    def _block(self):
        pass

    def _consume(self, token_name):
        token = self._lex.take()
        if token.name != token_name:
            pass

    def _recover(self):
        token = self._lex.take()
        while token.name not in ('eof', 'code'):
            token = self._lex.take()

#    def _error(self, token, message):
#        print("{}: error: {}".format(token.match





if __name__ == "__main__":
    from .lines import *
    import six
    s = Stream(six.StringIO("""\
# Doc 1
    
# Doc 2

function alama::kota {

}

# @func asdasdasa and go @there
#   sdsa
#       
# fdsfs
xyz()\
"""))

    p = Parser(s)
    print(p.parse())
