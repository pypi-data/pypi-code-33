from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from typhoon.utils import NoDuplicatesDict

from typhoon.license_typhoontest.manager import lic_check


# Check for license everytime typhoon.test is imported
lic_check()


def check_if_internal_capture(signal):
    if isinstance(signal, str):
        if capture is None:
            raise ValueError("Signal given as a string but there is no past captured data available yet.")
        else:
            signal = capture[signal]
    return signal

capture = None
marks = NoDuplicatesDict()


class wont_raise(object):
    """Used as a context manager where we don't expect any exception do be raised.
    Pytest still does not provide this out-of-the-box because of disagreements on naming.
    See: https://github.com/pytest-dev/pytest/issues/1830
    """
    def __init__(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, *excinfo):
        pass


def assert_td_list_approx(_list, list_ref, tol):
    if len(_list) != len(list_ref):
        raise AssertionError("Compared lists do not have same length.")
    for val, ref in zip(_list, list_ref):
        if not ref-tol <= val <= ref+tol:
            raise AssertionError("Value {} is not equal to {} within tolerance {}.".format(val, ref, tol))


