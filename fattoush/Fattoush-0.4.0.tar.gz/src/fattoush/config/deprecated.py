import contextlib
import functools
import warnings

import packaging.version

from fattoush.config.version import VERSION as _CURRENT


class VersionedDeprecation(Warning):
    template = "?!?"
    warning = DeprecationWarning

    def __new__(cls, version, reason):
        args = {
            'from': version,
            'current': _CURRENT,
            'reason': reason,
        }
        message = cls.template.format(**args)

        return cls.warning(message)


class NowDeprecated(VersionedDeprecation):
    template = "Deprecated since {from} (current: {current}): {reason}"
    warning = DeprecationWarning


class SoonDeprecated(VersionedDeprecation):
    template = "Will be deprecated in {from} (current: {current}): {reason}"
    warning = PendingDeprecationWarning


class FromVersion(object):
    def __init__(self, version, reason):
        self.version = packaging.version.parse(version)
        self.reason = reason

    def now(self):
        return NowDeprecated(self.version, self.reason)

    def later(self):
        return SoonDeprecated(self.version, self.reason)

    def check(self, stack_level=3):
        if _CURRENT >= self.version:
            raise self.now()

        with _always_warn():
            warnings.warn(self.later(), stacklevel=stack_level)

    def __enter__(self):
        self.check()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __call__(self, fn):
        @functools.wraps(fn)
        def _inner(*args, **kwargs):
            self.check()
            fn(*args, **kwargs)

        return _inner


@contextlib.contextmanager
def _always_warn():
    original = warnings.filters[:]

    warnings.resetwarnings()

    yield

    warnings.filters = original
