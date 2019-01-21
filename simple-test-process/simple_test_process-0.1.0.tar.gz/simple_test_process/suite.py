from .state import addSuite


def suite(label):
    def wrapper(fn):
        addSuite(label, fn)

    return wrapper
