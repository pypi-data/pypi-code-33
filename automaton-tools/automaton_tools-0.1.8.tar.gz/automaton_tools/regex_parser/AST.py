

class AST:
    def __init__(self):
        pass


class CharsetAST(AST):
    def __init__(self,charset):
        self.charset = charset

    def __repr__(self):
        temp = str(self.charset)
        if len(temp) == 1:
            return temp
        else :
            return f"{{{temp}}}"

class StarAST(AST):
    def __init__(self,content):
        super().__init__()
        self.content = content

    def __repr__(self):
        return f"({self.content})*" 

class PlusAST(AST):
    def __init__(self,content):
        super().__init__()
        self.content = content

    def __repr__(self):
        return f"({self.content})+" 

class OrAST(AST):
    def __init__(self,a,b):
        super().__init__()
        self.a = a
        self.b = b

    def __repr__(self):
        return f"({self.a}|{self.b})"

class RepeatAST(AST):
    def __init__(self,content,min,max):
        super().__init__()
        self.content = content
        self.min = min
        self.max = max

    def __repr__(self):
        if self.max is None:
            return f"{self.content}{{{self.min},}}" 
        else :
            return f"{self.content}{{{self.min},{self.max}}}" 

class OptionAST(AST):
    def __init__(self,content):
        super().__init__()
        self.content = content

    def __repr__(self):
        return f"({self.content})?"

class ConcatAST(AST):
    def __init__(self, a,b):
        super().__init__()
        self.a = a
        self.b = b

    def __repr__(self):
        return f"{self.a}{self.b}"