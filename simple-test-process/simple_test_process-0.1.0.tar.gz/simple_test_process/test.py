from .state import addTest


def test(label):
    def wrapper(fn):
        addTest(label, fn)

    return wrapper
