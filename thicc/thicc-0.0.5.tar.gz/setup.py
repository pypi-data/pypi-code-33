from setuptools import setup, find_packages
import codecs
import sys

from setuptools.command.test import test as TestCommand

import thicc


class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ""

    def run_tests(self):
        import shlex

        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


def long_description():
    with codecs.open("README.md", encoding="utf8") as f:
        return f.read()


setup(
    name="thicc",
    version=thicc.__version__,
    packages=find_packages(),
    url="https://github.com/t-mart/thicc",
    download_url="https://github.com/t-mart/thicc",
    license=thicc.__licence__,
    author=thicc.__author__,
    author_email="tim@timmart.in",
    description=thicc.__doc__.strip(),
    long_description=long_description(),
    long_description_content_type="text/markdown",
    entry_points={"console_scripts": ["thc = thicc.__main__:main"]},
    cmdclass={"test": PyTest},
    tests_require=["pytest"],
)
