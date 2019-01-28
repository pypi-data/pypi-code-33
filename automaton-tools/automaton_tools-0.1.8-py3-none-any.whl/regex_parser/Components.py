class State:
    def __init__(self,id=None):
        self.id = id

    def __repr__(self):
        if self.id is None:
            return "State(No id)"
        return str(self.id)

class AutomatonEdge:
    def match(self,other):
        pass

class EpsilonEdge(AutomatonEdge):
    def match(self,other):
        return True

    def __repr__(self):
        return 'ep'

    def __eq__(self, other):
        return type(other) is EpsilonEdge

    def __hash__(self):
        return hash("ep")

class CharSet(AutomatonEdge):
    def __init__(self,char):
        assert len(char) == 1, 'CharSet only accept a single char'
        self.char = char

    def match(self,other):
        return self.char == other

    def __eq__(self, other):
        if isinstance(other,CharSet):
            return other.char == self.char
        return False

    def __hash__(self):
        return hash(self.char)

    def __repr__(self):
        return self.char

class CharAny(CharSet):
    def __init__(self):
        pass
    def match(self, other):
        return True

    def __eq__(self, other):
        return isinstance(other,CharAny)

    def __hash__(self):
        return hash(".")

    def __repr__(self):
        return "."

class CharRange(CharSet):
    def __init__(self,charset,show:str = None, exclude = False):
        if not (isinstance(charset,set) or isinstance(charset,frozenset)):
            raise Exception('CharRange only accept set')
        self.show = show
        self.exclude = exclude
        self.charset = frozenset(charset)

    def __repr__(self):
        if self.show is not None:
            return self.show
        return "".join(sorted(list(self.charset)))

    def __eq__(self, other):
        if isinstance(other,CharRange):
            return other.charset == self.charset
        return False

    def __hash__(self):
        return hash(self.charset)

    def match(self, other):
        if  self.exclude:
            return other not in self.charset
        return other in self.charset

class CharWord(CharSet):
    def __init__(self):
        self.exclude = set(
            ['\\',' ','\t']
        )

    def match(self, other):
        if type(other) is str:
            return other not in self.exclude
        return True

    def __repr__(self):
        return "anychar"


class CharStart(CharSet):

    def __init__(self):
        pass
    def match(self, other):
        return type(other) is CharStart

    def __repr__(self):
        return "^"


class CharEnd(CharSet):

    def __init__(self):
        pass
    def match(self, other):
        return type(other) is CharEnd

    def __repr__(self):
        return "$"



Edge_Epsilon = EpsilonEdge()
Char_DIGIT = CharRange( set( map(lambda x: chr(ord('0') + x) ,range(0,10)) ),"\\\\d" )
Char_SPACE = CharRange( set( [' ','\t','\n'] ) )
Char_ANY = CharAny()
Char_START = CharStart()
Char_EOS = CharEnd()
Char_WORD = CharWord()
