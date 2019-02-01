#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import os
from os.path import split, join, isdir, isfile, abspath, dirname
import shutil
import tempfile
import unittest

__all__ = []


def find_path(varname, sentinal, subdir=None):
    """
    Looks for a directory using the environment variable given and raises an
    exception if it can't find the sentinal file.

    If subdir is set, it adds a sub directory to the directory found in
    the environment variable
    """

    dir = os.environ.get(varname, None)
    if not dir:
        raise Exception("%s is not set, cannot find test files" % varname)

    if subdir is not None:
        dir = join(dir, subdir)

    if not isdir(dir):
        raise Exception("%s is not a directory" % varname)

    # Our test file
    if not isfile(join(dir, sentinal)):
        raise Exception("%s does not seem to contain sentinal "
                        "file %s" % (varname, sentinal))

    return abspath(dir)


def anamtestpath():
    """Looks for the directory of anam test data relative to the
    current file"""
    d, f = split(__file__)
    return join(abspath(d), 'data')


def remove_file(filename):
    from os import unlink
    try:
        unlink(filename)
    except Exception:
        pass


def h5pytempfile():
    import h5py
    from tempfile import mkstemp
    from os import close

    fd, name = mkstemp()

    # This is a race condition but is as good as we can do at the moment
    close(fd)
    return h5py.File(name, 'w')


def array_assert(a, b, decimal=None, **kwargs):
    if decimal is None:
        if a.shape != b.shape:
            raise AssertionError("Sizes of matrices don't match "
                                 "(%s vs %s)" % (str(a.shape), str(b.shape)))

        if ((a == b).all()):
            return

        # Otherwise give some info as to why we're asserting
        raise AssertionError("Arrays are not the same:\n"
                             "Array A:%s\nArray B:%s" % (a, b))
    else:
        from numpy.testing import assert_almost_equal
        assert_almost_equal(a, b, decimal, *kwargs)


__all__.append('array_assert')


class AnamTestBase(unittest.TestCase):
    """
    Use when an output directory is needed to write test files into
    """
    def setUp(self):
        self.preSetUp()
        self.tempdir = tempfile.mkdtemp()
        if 'ANAMDEBUG' in os.environ:
            print("Temporary directory: ", self.tempdir)
        self.postSetUp()

    @property
    def anamtestdir(self):
        return anamtestpath()

    def preSetUp(self):
        pass

    def postSetUp(self):
        pass

    def tearDown(self):
        self.preTearDown()
        if 'ANAMDEBUG' in os.environ:
            print("Not removing temporary directory "
                  "%s as ANAMDEBUG is set" % self.tempdir)
        else:
            shutil.rmtree(self.tempdir)
        self.postTearDown()

    def preTearDown(self):
        pass

    def postTearDown(self):
        pass

    def mkdir(self, dirname):
        from errno import EEXIST
        abs_dirname = join(self.tempdir, dirname)
        try:
            os.makedirs(abs_dirname)
        except OSError as e:
            if e.errno != EEXIST:
                raise e

        return abs_dirname

    def copyfile(self, frompath, relto):
        self.mkdir(dirname(relto))
        abs_to = join(self.tempdir, relto)
        shutil.copyfile(frompath, abs_to)

    def check_file_exists(self, filename):
        abs_filename = join(self.tempdir, filename)
        os.stat(abs_filename)


__all__.append('AnamTestBase')
