#Copyright 2018 Jonathan Sacramento

#This file is part of sassy.
#
#sassy is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#sassy is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with sassy. If not, see <http://www.gnu.org/licenses/>.

from .error import *
from .token import Token
from .tokentype import TokenType


class Scanner(object):

    def __init__(self, source):
        self.source = source
        self.tokens = []

        self._start = 0
        self._current = 0
        self._line = 1
        self.keywords = {
            '%macro': TokenType.MACRO_START,
            '%mend': TokenType.MACRO_END,
            '%let': TokenType.LET,
            '%procloop': TokenType.LOOP_START,
            '%pend': TokenType.PROC_END,
            '%exec': TokenType.EXEC
        }

    def scan(self):
        while not self._is_at_end():
            self._start = self._current
            self.scan_token()

        return self.tokens

    def scan_token(self):
        c = self._advance()
        if c == '(':
            self.add_token(TokenType.LEFT_PAREN)
        elif c == ')':
            self.add_token(TokenType.RIGHT_PAREN)
        elif c == '{':
            self.add_token(TokenType.LEFT_BRACE)
        elif c == '}':
            self.add_token(TokenType.RIGHT_BRACE)
        elif c == ',':
            self.add_token(TokenType.COMMA)
        elif c == '.':
            self.add_token(TokenType.DOT)
        elif c == '-':
            self.add_token(TokenType.MINUS)
        elif c == '+':
            self.add_token(TokenType.PLUS)
        elif c == ';':
            self.add_token(TokenType.SEMICOLON)
        elif c == '*':
            self.add_token(TokenType.STAR)
        # elif c == '%':
        #     self.add_token(TokenType.PERCENT)
        elif c == '$':
            self.add_token(TokenType.DOLLAR)
        elif c == '#':
            self.add_token(TokenType.HASH)
        elif c == '@':
            self.add_token(TokenType.AT)
        elif c == '|':
            self.add_token(TokenType.PIPE)
        elif c == '&':
            self.add_token(TokenType.AMPERSAND)
        elif c == ':':
            self.add_token(TokenType.COLON)
        elif c == '?':
            self.add_token(TokenType.QUESTION_MARK)
        elif c == '[':
            self.add_token(TokenType.LEFT_SQR_PAREN)
        elif c == ']':
            self.add_token(TokenType.RIGHT_SQR_PAREN)
        elif c == '!':
            self.add_token(
                TokenType.BANG_EQUAL if self._match('=') else TokenType.BANG)
        elif c == '=':
            self.add_token(
                TokenType.EQUAL_EQUAL if self._match('=') else TokenType.EQUAL)
        elif c == '<':
            self.add_token(
                TokenType.LESS_EQUAL if self._match('=') else TokenType.LESS)
        elif c == '>':
            self.add_token(
                TokenType.GREATER_EQUAL if self._match('=') else TokenType.GREATER)
        elif c == '/':
            if self._match('/'):
                while (self._peek() != '\n' and not self._is_at_end()):
                    self._advance()
            else:
                self.add_token(TokenType.SLASH)
        elif c == ' ':
            self.add_token(TokenType.SPACE)
        elif c == '\r':
            self.add_token(TokenType.CARRIAGE_RETURN)
        elif c == '\t':
            self.add_token(TokenType.TAB)
        elif c == '\n':
            self.add_token(TokenType.NEW_LINE)
            self._line += 1
        elif c == '"':
            self.identifier()
        elif c == '\'':
            self.identifier()
        elif self._is_digit(c):
            self.number()
        elif self._is_alpha(c):
            self.identifier()
        else:
            self._scan_error(self._line, self._current, 'Unexpected character.')

    def _scan_error(self, line, where, message):
        errorText = '[line {line} char {where}] Error: {message}'.format(
            line=line,
            where=where,
            message=message
        )
        errorSource  = self.source
        errorPointer = ' ' * (int(where) - 1)
        errorPointer += '^'

        errorMsg = errorText + '\n' + errorSource + errorPointer + '\n'
        raise ScanError(errorMsg)

    def _is_at_end(self):
        return self._current >= len(self.source)

    def identifier(self):
        while self._is_alpha_numeric(self._peek()):
            self._advance()
        text = self.source[self._start:self._current]
        token_type = self.keywords.get(text)
        if token_type is None:
            token_type = TokenType.IDENTIFIER

        self.add_token(token_type)

    def number(self):
        while self._is_digit(self._peek()):
            self._advance()

        if self._peek() == '.' and self._is_digit(self._peek_next()):
            # consume the dot
            self._advance()
            while self._is_digit(self._peek()):
                self._advance()

        self.add_token(
            TokenType.NUMBER, float(self.source[self._start:self._current]))

    def string(self):
        while self._peek() != '"' and not self._is_at_end():
            if self._peek == '\n':
                self._line += 1
            self._advance()

        # unterminated string
        if self._is_at_end():
            self._scan_error(self._line, self._current, 'Unterminated string.')

        self._advance()
        value = self.source[self._start + 1:self._current - 1]
        self.add_token(TokenType.STRING, value)

    def _is_digit(self, c):
        return c.isdigit()

    def _is_alpha(self, c):
        return c.isalpha() or c == '_' or c == '%'

    def _is_alpha_numeric(self, c):
        return self._is_alpha(c) or self._is_digit(c)

    def _match(self, expected):
        if self._is_at_end():
            return False

        if self.source[self._current] != expected:
            return False

        self._current += 1
        return True

    def _peek(self):
        if self._current >= len(self.source):
            return '\0'
        return self.source[self._current]

    def _peek_next(self):
        if (self._current + 1) >= len(self.source):
            return '\0'
        return self.source[self._current + 1]

    def _advance(self):
        self._current += 1
        return self.source[self._current - 1]

    def add_token(self, token_type, literal=None):
        text = self.source[self._start:self._current]
        self.tokens.append(Token(token_type, text, literal, self._line))
