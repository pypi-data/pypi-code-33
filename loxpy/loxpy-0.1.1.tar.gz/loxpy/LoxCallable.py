from typing import List


class LoxCallable:
    def arity(self) -> int:
        pass

    def call(self, interpreter: "Interpreter", arguments: List[object]) -> object:
        pass
