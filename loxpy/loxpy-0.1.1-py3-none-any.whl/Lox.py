import sys
from typing import TypeVar

# static check
from . import Interpreter
from . import ErrorState
from .Scanner import Scanner
from . import Parser

ErrorState.hadError = False
ErrorState.hadRuntimeError = False
T = TypeVar("T")

interpreter = Interpreter.Interpreter()  # REVIEW: keep REPL session


def main():
    if len(sys.argv) > 2:
        print("Usage: plox [script]")
    elif len(sys.argv) == 2:
        runFile(sys.argv[1])
    else:
        runPrompt()


def runFile(path: str):
    run(open(path, "r", encoding="utf-8").read())
    if ErrorState.hadError:
        sys.exit(65)
    if ErrorState.hadRuntimeError:
        sys.exit(70)


def runPrompt():
    bang = ">"
    lines = []
    while True:
        lines.append(input(f"{bang} "))
        if lines[-1].endswith("\\"):
            lines[-1] = lines[-1].rstrip("\\")
            bang = ":"
        else:
            run(" ".join(lines))
            lines = []
            bang = ">"


def run(source: str):
    scanner = Scanner(source)
    tokens = scanner.scanTokens()
    # for token in tokens:
    #     print(token)
    parser = Parser.Parser(tokens)
    statements = parser.parse()

    if ErrorState.hadError:
        return

    interpreter.interpreter(statements)


# Map<String, TokenType>

