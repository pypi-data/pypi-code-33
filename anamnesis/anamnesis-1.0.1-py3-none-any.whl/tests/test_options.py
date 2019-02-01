#!/usr/bin/python

"""Tests for options module"""
# vim: set expandtab ts=4 sw=4:

import sys

# Deal with gratuitous changes in str/bytes/unicode between python 2 and 3 I'm
# sure it's all nice and neat now - and a complete pain if you live in the real
# world and have to support both simultaneously.
if sys.version_info.major == 2:
    from io import BytesIO as StringIO
else:
    from io import StringIO

from ..test import AnamTestBase  # noqa: E402


class OptionsTest(AnamTestBase):
    def test_init_options(self):
        """Check that we can initialise a the global AnamOptions object"""
        from ..options import AnamOptions
        a = AnamOptions()
        assert(isinstance(a, AnamOptions))

    def test_empty_store_equality(self):
        """Check that we can set and get the verbose and progress options"""
        from ..options import AnamOptions
        a = AnamOptions()

        # Check we default to 0
        assert(a.verbose == 0)
        assert(a.progress == 0)

        # Increment both
        a.verbose += 1
        a.progress += 2

        # We should see this on another "instance" of the object
        b = AnamOptions()
        assert(b.verbose == 1)
        assert(b.progress == 2)

        # Put them back
        b.verbose = 0
        b.progress = 0

    def test_write_progress(self):
        """Check that we write appropriately with progress set"""
        from ..options import AnamOptions
        a = AnamOptions()
        a.progress = 0

        s = StringIO()
        a.write_progress("Should not be written", target=s)
        s.seek(0)
        assert(len(s.read()) == 0)
        s.close()

        # And now when we should get something
        a.progress = 1
        s = StringIO()
        a.write_progress("Should be written", target=s)
        s.seek(0)
        t = s.read()
        assert(t == "Should be written")
        s.close()

    def test_write_verbose(self):
        """Check that we write appropriately with verbose set"""
        from ..options import AnamOptions
        a = AnamOptions()
        a.verbose = 0

        s = StringIO()
        a.write("Should not be written", target=s)
        s.seek(0)
        assert(len(s.read()) == 0)
        s.close()

        # And now when we should get something
        a.verbose = 1
        s = StringIO()
        a.write("Should be written", target=s)
        s.seek(0)
        t = s.read()
        assert(t == "Should be written")
        s.close()
