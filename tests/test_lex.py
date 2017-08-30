
import six

from shdoc.lines import *
from shdoc.lex import *

def test_peek_does_not_consume_token(capsys):
    data = six.StringIO("""\
#
""")

    lex = Lexer(Stream(data))

    with capsys.disabled():
        print(lex.peek(None))
        print("asdas")


    
