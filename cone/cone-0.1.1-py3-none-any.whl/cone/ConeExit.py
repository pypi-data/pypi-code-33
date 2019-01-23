from __future__ import print_function

import sys


def print_error(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class ConeExit(Exception):

    def __init__(self, out="", error_out=""):
        self.out = out
        self.error_out = error_out

    @staticmethod
    def error(error_out):
        return ConeExit(error_out=error_out)

    @staticmethod
    def fromResult(result):
        if "out" in result.keys() and "error_out" in result.keys():
            return ConeExit(out=result["out"], error_out=result["error_out"])
        else:
            return ConeExit(error_out="Unexpected result (received: {})".format(result))

    def print(self):
        if len(self.out) > 0:
            print(self.out)
        if len(self.error_out) > 0:
            print_error(self.error_out)
