from .LoxRuntimeError import LoxRuntimeError
from .Tokens import Token


class Environment:
    def __init__(self, enclosing=None):  # None for global scope's environment
        self.enclosing: Environment = enclosing
        self.values = {}

    def define(self, name: str, value: object):
        self.values[name] = value

    def get(self, name: Token):
        """get name in current scope or outer scope"""
        if name.lexeme in self.values.keys():
            return self.values.get(name.lexeme)
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}' .")

    def assign(self, name: Token, value: object):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing is not None:  # 允许修改外部作用域的变量的值
            self.enclosing.values[name.lexeme] = value
            return
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
