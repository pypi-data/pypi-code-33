import unittest
import os
import sys
import tempfile

from fluiddevops.util import run, logger, chdir, Path, rmtree
from fluiddevops import mirror


# Skip when the python 3 is used in continuous integration
# SKIP_TEST = sys.version_info >= (3,) and os.getenv("CI", False)
SKIP_TEST = "CI" in os.environ


class TestMirror(unittest.TestCase):
    @classmethod
    def setUpClass(cls, hggit=False):
        workdir = Path(tempfile.gettempdir()) / cls.__name__
        logger.info("Test directory {}".format(workdir))

        cls.workdir = workdir.absolute()

        # Remote
        cls.hg = "test_hg_repo"
        cls.git = "test_git_repo"
        cls.rhg = cls.workdir / cls.hg
        cls.rgit = cls.workdir / cls.git

        # Local
        cls.subdir = cls.workdir / "subdir"
        cls.lhg = cls.subdir / cls.hg
        cls.lgit = cls.subdir / cls.git

        cls.parse = mirror.get_parser().parse_args
        cls.user = "CI <someone@example.com>"

        for d in (cls.workdir, cls.subdir):
            if not d.exists():
                d.mkdir()

        chdir(cls.workdir)
        run("hg init {}".format(cls.hg))
        run("git init {}".format(cls.git))
        cls.git_config(cls.rgit)

        chdir(cls.subdir)
        mirror.init_config(
            cls.subdir / "mirror.cfg",
            pull_base=str(cls.workdir),
            push_base=str(cls.workdir),
            repos=(cls.hg, cls.git),
            hggit=hggit,
        )
        mirror._clone_all(cls.parse(["clone"]))
        cls.git_config(cls.lgit)

    @classmethod
    def tearDownClass(cls):
        chdir(cls.workdir.parent)
        rmtree(cls.workdir)

    @classmethod
    def git_config(cls, git):
        chdir(git)
        run("git config --local user.name {}".format(cls.user.split()[0]))
        run("git config --local user.email {}".format(cls.user.split()[1]))
        run("git config --local push.default simple")

    def change(self, hg, git, hggit=False):
        chdir(hg)
        hello = hg / "hello.txt"
        hello.touch()
        run("hg addr")
        run("hg ci -m 'Add a file' -u '{}'".format(self.user))

        chdir(git)
        hello = git / "hello.txt"
        hello.touch()
        if hggit:
            run("hg addr")
            run("hg ci -m 'Add a file' -u '{}'".format(self.user))
        else:
            run("git add {}".format(hello))
            run("git commit -m 'Add a file'")

    def test_set_remote(self):
        chdir(self.subdir)
        mirror._setr_all(self.parse(["set-remote"]))

    def test_pull(self):
        self.change(self.rhg, self.rgit)
        chdir(self.subdir)
        mirror._pull_all(self.parse(["pull"]))

    def test_sync(self):
        self.change(self.rhg, self.rgit)
        chdir(self.subdir)
        mirror._sync_all(self.parse(["sync"]))

    def test_push(self):
        self.change(self.lhg, self.lgit)
        chdir(self.subdir)
        mirror._push_all(self.parse(["push"]))

    def test_run(self):
        chdir(self.subdir)

        mirror._run_all(self.parse(["run", "-r", str(self.hg), "hg", "st"]))
        chdir(self.lhg)
        mirror._run_all(self.parse(["run", "ls"]))


@unittest.skipIf(SKIP_TEST, "Fails in CI")
class TestMirrorHgGit(TestMirror):
    @classmethod
    def setUpClass(cls):
        super(TestMirrorHgGit, cls).setUpClass(hggit=True)

    def test_push(self):
        self.change(self.lhg, self.lgit, hggit=True)
        chdir(self.subdir)
        mirror._push_all(self.parse(["push"]))


if __name__ == "__main__":
    unittest.main()
