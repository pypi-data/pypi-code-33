import threading
import contextlib

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.3"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ['load_mark']


CONTEXT_MARKS = threading.local()
CONTEXT_MARKS.load = False


@contextlib.contextmanager
def load_mark():
    original_mark = getattr(CONTEXT_MARKS, 'load', False)
    try:
        CONTEXT_MARKS.load = True
        yield
    except Exception:
        CONTEXT_MARKS.load = original_mark
        raise
    else:
        CONTEXT_MARKS.load = original_mark
