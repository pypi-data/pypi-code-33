# usr/bin env python3
# coding: utf-8

from .Tokens import Token, TokenType
from . import ErrorState


class ParseError(Exception):
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message

    def report(self):
        if self.token.type == TokenType.EOF:
            print(f'[line {self.token.line}] Error at end: {self.message}')
        else:
            where = self.token.lexeme
            print(f"[line {self.token.line}] Error at '{where}': {self.message}")

        ErrorState.hadError = True
