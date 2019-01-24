from builtins import str

import unittest
import os

from fluiddevops.util import run, logger, chdir, Path, rmtree
from fluiddevops import icat


class TestICat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workdir = Path("test_icat").absolute()
        cls.workfile = cls.workdir / "numbers.txt"
        cls.parse = icat.get_parser().parse_args

        if not cls.workdir.exists():
            cls.workdir.mkdir()
        chdir(cls.workdir)

    @classmethod
    def tearDownClass(cls):
        chdir(cls.workdir.parent)
        rmtree(cls.workdir)

    def test_input_file(self):
        self.workfile.write_text("\n".join([str(i) for i in range(10)]))
        args = self.parse([str(self.workfile)])
        icat.main(args)


if __name__ == "__main__":
    unittest.main()
