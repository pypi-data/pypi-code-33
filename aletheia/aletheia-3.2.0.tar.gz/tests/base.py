import collections
import logging
import os
import shutil
import tempfile
from unittest import TestCase as BaseTestCase

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    load_pem_public_key
)


class TestCase(BaseTestCase):

    DATA = os.path.join(os.path.dirname(__file__), "data")

    # A hash of example.com
    EXAMPLE_DOT_COM = "020506e9b65ec049e227e0a25dfafa84ebfc8eb366b6ce9731d757ae96ee223a14c0a51d6d8a72d45b71b6c779f2dd58841f29180827096a129145c5bcf608e6"  # NOQA: E501

    def __init__(self, *args):
        super(TestCase, self).__init__(*args)
        logging.basicConfig(level=logging.DEBUG)

    def setUp(self):
        self.scratch = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.scratch, "public-keys"), exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.scratch, ignore_errors=True)

    def get_private_key(self):
        with open(os.path.join(self.DATA, "keys", "private.pem"), "rb") as f:
            return load_pem_private_key(f.read(), None, default_backend())

    def get_public_key(self):
        with open(os.path.join(self.DATA, "keys", "public.pkcs1"), "rb") as f:
            return load_pem_public_key(f.read(), default_backend())

    def cache_public_key(self) -> str:
        cache = os.path.join(self.scratch, "public-keys")
        shutil.copy(
            os.path.join(self.DATA, "keys", "public.pkcs1"),
            os.path.join(cache, self.EXAMPLE_DOT_COM)
        )
        return cache

    def copy_for_work(self, directory: str, type_: str) -> str:
        """
        Copy our test file to ``scratch`` so we can fiddle with it.
        """
        path = os.path.join(self.scratch, "test.{}".format(type_))
        shutil.copyfile(
            os.path.join(self.DATA, directory, "test.{}".format(type_)),
            path
        )
        return path


class EnvironmentVarGuard(collections.abc.MutableMapping):

    """
    Copied straight out of the test module that's only sometimes available with
    Python for some reason.
    """

    def __init__(self):
        self._environ = os.environ
        self._changed = {}

    def __getitem__(self, envvar):
        return self._environ[envvar]

    def __setitem__(self, envvar, value):
        # Remember the initial value on the first access
        if envvar not in self._changed:
            self._changed[envvar] = self._environ.get(envvar)
        self._environ[envvar] = value

    def __delitem__(self, envvar):
        # Remember the initial value on the first access
        if envvar not in self._changed:
            self._changed[envvar] = self._environ.get(envvar)
        if envvar in self._environ:
            del self._environ[envvar]

    def keys(self):
        return self._environ.keys()

    def __iter__(self):
        return iter(self._environ)

    def __len__(self):
        return len(self._environ)

    def set(self, envvar, value):
        self[envvar] = value

    def unset(self, envvar):
        del self[envvar]

    def __enter__(self):
        return self

    def __exit__(self, *ignore_exc):
        for (k, v) in self._changed.items():
            if v is None:
                if k in self._environ:
                    del self._environ[k]
            else:
                self._environ[k] = v
        os.environ = self._environ
