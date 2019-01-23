import functools
import pytest
from multiprocessing import Pool

def _check_one_depend(depend):
    try:
        depend()
    except Exception as e:
        return False
    else:
        return True

def another_interp_check_depends(depends):
    with Pool(min(len(depends), 4)) as pl:
        results = pl.map(_check_one_depend, depends)
        if not all(results):
            return depends[results.index(False)]
        else:
            return True

def check_depends(depends):
    try:
        for dep in depends:
            dep()
    except Exception as e:
        return dep
    else:
        return True

def pytest_depend(depends):
    def pytest_depend_decorator(func):
        stat = check_depends(depends)
        if stat is True:
            return func
        else:
            return pytest.mark.skip(True, reason="%s[skip] --> %s[Failed]" % (func.__name__, stat.__name__))(func)
    return pytest_depend_decorator

def pytest_safe_depend(depends):
    def pytest_depend_decorator(func):
        stat = another_interp_check_depends(depends)
        if stat is True:
            return func
        else:
            return pytest.mark.skip(True, reason="%s[skip] --> %s[Failed]" % (func.__name__, stat.__name__))(func)
    return pytest_depend_decorator


