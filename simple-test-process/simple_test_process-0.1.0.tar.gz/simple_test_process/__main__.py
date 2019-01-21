from .runProcess import runProcess
import sys


def printErr(msg):
    print(msg, file=sys.stderr)


result = runProcess(*sys.argv[1:])

if result.stdout:
    print(result.stdout)

if result.stderr:
    printErr(result.stderr)

exit(result.code)
