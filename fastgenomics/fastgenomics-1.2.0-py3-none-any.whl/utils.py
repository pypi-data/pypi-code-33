import re


def str_normalize(input):
    reg = r"[A-Za-z0-9_]"
    return "".join([i for i in input if re.match(reg, i)])
