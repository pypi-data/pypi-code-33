import random
import string


def get_rand_str(l):
    t = ''.join(random.SystemRandom().choice(string.hexdigits) for _ in range(l))
    return t.lower()
