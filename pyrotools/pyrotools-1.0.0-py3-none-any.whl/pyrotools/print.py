from json import dumps

from pyrotools import _constants


def cprint(color, *values):
    print(color, end="", flush=True)
    for value in values:
        print(value, end=" ", flush=True)
    print(_constants.COLORS.RESET)


def pprint(var):
    print(dumps(var, sort_keys=True, indent=3))


def cpprint(color, var):
    print(color, end="", flush=True)
    pprint(var)
    print(_constants.COLORS.RESET)
