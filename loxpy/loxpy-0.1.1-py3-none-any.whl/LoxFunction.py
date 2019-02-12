from typing import List

from . import Stmt
from .Environment import Environment
from .LoxCallable import LoxCallable
from .Return import Return


class LoxFunction(LoxCallable):
    def __init__(self, declaration: Stmt.Function, closure: Environment):
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter: "Interpreter", arguments: List[object]):
        environment = Environment(self.closure)
        for i in range(len(self.declaration.parameters)):
            environment.define(self.declaration.parameters[i].lexeme, arguments[i])

        try:
            interpreter.executeBlock(self.declaration.body, environment)
        except Return as returnValue:
            return returnValue.value

    def arity(self):
        return len(self.declaration.parameters)

    def __str__(self):
        return f"<function {self.declaration.name.lexeme} >"
