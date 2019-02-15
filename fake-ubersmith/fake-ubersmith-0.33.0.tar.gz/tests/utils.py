import random
import string


def a_random_string(length=8):
    return ''.join(random.sample(string.ascii_lowercase, k=length))
