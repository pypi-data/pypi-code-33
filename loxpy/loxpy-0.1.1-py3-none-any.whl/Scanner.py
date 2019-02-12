# usr/bin env python3
# coding: utf-8
from typing import List
from .ScannerError import ScanError
from .Tokens import Token, TokenType


class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.tokens = []  # List<Token>

        self.start = 0
        self.current = 0
        self.line = 1

    def scanTokens(self) -> List[Token]:
        while not self.isAtEnd():
            self.start = self.current
            self.scanToken()
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def isAtEnd(self) -> bool:
        return self.current >= len(self.source)

    def scanToken(self):
        c = self.advance()
        if c == '(':
            self.addToken(TokenType.LEFT_PAREN)
        elif c == ')':
            self.addToken(TokenType.RIGHT_PAREN)
        elif c == '{':
            self.addToken(TokenType.LEFT_BRACE)
        elif c == '}':
            self.addToken(TokenType.RIGHT_BRACE)
        elif c == ',':
            self.addToken(TokenType.COMMA)
        elif c == '.':
            self.addToken(TokenType.DOT)
        elif c == '-':
            self.addToken(TokenType.MINUS)
        elif c == '+':
            self.addToken(TokenType.PLUS)
        elif c == ';':
            self.addToken(TokenType.SEMICOLON)
        elif c == '*':
            self.addToken(TokenType.STAR)

        elif c == '!':
            self.addToken(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
        elif c == '=':
            self.addToken(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
        elif c == '<':
            self.addToken(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
        elif c == '>':
            self.addToken(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)

        # slash 需要特别处理
        elif c == '/':
            if self.match('/'):
                while self.peek() != '\n' and not self.isAtEnd(): self.advance()
            else:
                self.addToken(TokenType.SLASH)

        # 忽略空白字符
        elif c == ' ':
            pass
        elif c == '\r':
            pass
        elif c == '\t':
            pass
        elif c == '\n':
            self.line += 1

        elif c == '"':
            self.string()
        else:
            # 处理数字
            if self.isDigit(c):
                self.number()
            # 处理关键词，方式和处理 <= 相似
            elif self.isAlpha(c):
                self.identifier()
            else:
                self.error(self, "Unexpected character.")

    def advance(self) -> str:
        """**consume**
        return current char and go to next
         consumes the next character in the source file and returns it"""
        self.current += 1
        return self.source[self.current - 1]

    def addToken(self, token_type: TokenType, literal: object = None):
        text = self.source[
               self.start:self.current]  # REVIEW: self.start:self.current 写成了 self.current:self.current 前缀符号丢失
        self.tokens.append(Token(token_type, text, literal, self.line))

    def match(self, expected):
        if self.isAtEnd(): return False  # 位置
        if self.source[self.current] != expected:  # 匹配
            return False
        self.current += 1
        return True

    def peek(self):  # REVIEW: match 和 peek 的功能的差别, match 消耗字符，peek 否
        """**lookahead**
        look but not consume"""
        if self.isAtEnd(): return '\0'  # Q: 为什么要返回 \0
        return self.source[self.current]

    def string(self):
        while self.peek() != '"' and not self.isAtEnd():  # review: 这里的 while 之前错写为 if 导致直接收一个字符
            if self.peek() == '\n': self.line += 1  # 允许字符串跨行
            self.advance()

        # 未正常终结
        if self.isAtEnd():
            self.error(self, "Unterminated string.")
            return

        # 正常闭合 '"'
        self.advance()
        # 这里去掉了两边的 “
        value = self.source[self.start + 1: self.current - 1]  # review: 为什么是 start+1，start 代表着一个 token 的开始
        self.addToken(TokenType.STRING, value)

    def isDigit(self, c: str):
        return '0' <= c <= '9'

    def number(self):
        """match 12345 or 12345.1234
        but not .123 or 1234."""

        while self.isDigit(self.peek()): self.advance()

        # 处理浮点数部分，消耗 “.”
        if self.peek() == '.' and self.isDigit(self.peekNext()):
            self.advance()

            while self.isDigit(self.peek()): self.advance()

        self.addToken(TokenType.NUMBER,
                      float(self.source[self.start: self.current]))

    def peekNext(self) -> str:
        if self.current + 1 > len(self.source): return '\0'
        return self.source[self.current + 1]

    def identifier(self):
        while self.isAlphaNumeric(self.peek()): self.advance()
        # self.addToken(TokenType.IDENTIFIER)

        # review 判断标识符是否为保留字
        text = self.source[self.start: self.current]
        token_type = keywords.get(text)
        if token_type is None: token_type = TokenType.IDENTIFIER
        self.addToken(token_type)

    def isAlpha(self, c: str):
        return 'a' <= c <= 'z' or 'A' <= c <= 'Z' or c == '_'

    def isAlphaNumeric(self, c):
        return self.isAlpha(c) or self.isDigit(c)

    def error(self,token, message):
        err = ScanError(self.line, message)
        err.report()



keywords = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "for": TokenType.FOR,
    "fun": TokenType.FUN,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
}
