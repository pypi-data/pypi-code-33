from .cli import runSimpleTest
from .run import run
import sys


def printErr(msg):
    print(msg, file=sys.stderr)


def main():
    result = runSimpleTest(run, sys.argv[1:])

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        printErr(result.stderr)

    exit(result.code)
