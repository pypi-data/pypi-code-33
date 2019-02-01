from json import dumps

from pyrotools import constants


def cprint(color, *values):
    print(color, end="", flush=True)
    for value in values:
        print(value, end=" ", flush=True)
    print(constants.COLORS.RESET)


def pprint(var):
    print(dumps(var, sort_keys=True, indent=3))


def cpprint(color, var):
    print(color, end="", flush=True)
    pprint(var)
    print(constants.COLORS.RESET)
