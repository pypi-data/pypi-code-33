from enum import Enum, auto


class TokenType(Enum):
    LEFT_PAREN, RIGHT_PAREN, LEFT_BRACE, RIGHT_BRACE = [auto() for i in range(4)]
    COMMA, DOT, MINUS, PLUS, SEMICOLON, SLASH, STAR = [auto() for i in range(7)]

    # One or two character tokens.
    BANG, BANG_EQUAL = [auto() for i in range(2)]
    EQUAL, EQUAL_EQUAL = [auto() for i in range(2)]
    GREATER, GREATER_EQUAL = [auto() for i in range(2)]
    LESS, LESS_EQUAL, = [auto() for i in range(2)]

    # Literals.
    IDENTIFIER, STRING, NUMBER, = [auto() for i in range(3)]

    # Keywords.
    AND, CLASS, ELSE, FALSE, FUN, FOR, IF, NIL, OR, = [auto() for i in range(9)]
    PRINT, RETURN, SUPER, THIS, TRUE, VAR, WHILE, = [auto() for i in range(7)]

    EOF = auto()

    # REVIEW: 这里犯了一个非常糟糕的错误，[auto()] 产生不能区分数值的列表，导致标识符完全无法区分


class Token:

    def __init__(self, type: TokenType, lexeme: str, literal: object, line: int):
        self.type, self.lexeme, self.literal, self.line = type, lexeme, literal, line

    def __str__(self):
        return '%s %s %s' % (self.type, self.lexeme, self.literal)

    def __repr__(self):
        args = f'{self.type}, {self.lexeme}, {self.literal}, {self.line}'
        return f'{self.__class__.__name__}({args})'
