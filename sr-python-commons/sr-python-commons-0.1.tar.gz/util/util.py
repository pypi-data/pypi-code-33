import random
import time
import traceback
import hashlib
import inspect
from contextlib import contextmanager
from functools import wraps


def md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()


def get_nonce(length=10):
    number = round(time.time() * 10)
    return int(str(number)[-length:])


def get(val, default_val):
    return val if val else default_val


def get_caller():
    return inspect.currentframe().f_back.f_locals['self']
