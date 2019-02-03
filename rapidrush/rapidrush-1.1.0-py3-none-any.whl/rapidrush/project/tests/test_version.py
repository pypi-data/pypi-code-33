SOURCEHEADER

import os
import re
import sys
import subprocess
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PACKAGENAME.utils.version import (
    git_commit_count,
    git_commit_date,
    git_commit_hash,
    git_describe,
)


def is_canonical(version):
    return (
        re.match(
            r"^([1-9]\d*!)?(0|[1-9]\d*)(\.(0|[1-9]\d*))*((a|b|rc)(0|[1-9]\d*))?"
            "(\.post(0|[1-9]\d*))?(\.dev(0|[1-9]\d*))?$",
            version,
        )
        is not None
    )


class TestVersion(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.version = __import__("PACKAGENAME").__version__
        self.commit_hash = git_commit_hash()
        self.commit_date = git_commit_date()
        self.commit_count = git_commit_count()
        self.commit_describe = git_describe()

    @classmethod
    def tearDownClass(self):
        pass

    def test_get_version(self):
        self.assertTrue(is_canonical(self.version))

    def test_git_commit_hash(self):
        self.assertTrue(self.commit_hash)

    def test_git_commit_date(self):
        self.assertTrue(self.commit_date)

    def test_git_describe(self):
        self.assertTrue(self.commit_describe)


if __name__ == "__main__":
    unittest.main()
