from pytest import fixture

from collections import namedtuple
from pathlib import Path
from shutil import rmtree


KIRLENT_ROOT = Path("/dev/shm/kirlent")


SrcOutPaths = namedtuple("Paths", ["src", "out"])


@fixture(scope="session")
def kirlent_env():
    """Source and build paths for the entire content."""
    src_root = Path(KIRLENT_ROOT, "content")
    out_root = Path(src_root.parent, "_build")

    rmtree(KIRLENT_ROOT, ignore_errors=True)
    KIRLENT_ROOT.mkdir(parents=True)

    src_root.mkdir()

    yield SrcOutPaths(src_root, out_root)

    rmtree(KIRLENT_ROOT)


@fixture
def unit1(kirlent_env):
    """Source and build paths of a unit with slides."""
    src, out = Path(kirlent_env.src, "unit1"), Path(kirlent_env.out, "unit1")
    rmtree(src, ignore_errors=True)
    rmtree(out, ignore_errors=True)
    src.mkdir()

    Path(src, "slides.en.rst").write_text("")

    yield SrcOutPaths(src, out)

    rmtree(src, ignore_errors=True)
    rmtree(out, ignore_errors=True)


@fixture
def unit2(kirlent_env):
    """Source and build paths of a unit with slides."""
    src, out = Path(kirlent_env.src, "unit2"), Path(kirlent_env.out, "unit2")
    rmtree(src, ignore_errors=True)
    rmtree(out, ignore_errors=True)
    src.mkdir()

    Path(src, "slides.en.rst").write_text("")

    yield SrcOutPaths(src, out)

    rmtree(src, ignore_errors=True)
    rmtree(out, ignore_errors=True)


@fixture
def unit3(kirlent_env, unit1, unit2):
    """Source and build paths of a unit with parts."""
    src, out = Path(kirlent_env.src, "unit3"), Path(kirlent_env.out, "unit3")
    rmtree(src, ignore_errors=True)
    rmtree(out, ignore_errors=True)
    src.mkdir()

    Path(src, "parts.txt").write_text("unit1\nunit2\n")

    yield SrcOutPaths(src, out)

    rmtree(src, ignore_errors=True)
    rmtree(out, ignore_errors=True)
