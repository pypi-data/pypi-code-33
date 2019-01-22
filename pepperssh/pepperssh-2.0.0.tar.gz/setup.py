#!/usr/bin/env python

import sys
from distutils.core import setup, Command

VERSION = '2.0.0'


class TestCommand(Command):
    user_options = [('pytest-args=', 'a', 'Arguments to pass to pytest')]

    def initialize_options(self):
        self.pytest_args = ''

    def finalize_options(self):
        pass

    def run(self):
        import shlex
        try:
            import pytest
        except ImportError:
            sys.exit('pytest not found (Try pip install pytest)')
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


setup(
    name='pepperssh',
    description='Simple SSH based remote execution',
    version=VERSION,
    #  package_dir={'': 'pepperssh'},
    packages=['pepperssh'],
    author='Michael Kleehammer',
    author_email='michael@kleehammer.com',
    url='https://gitlab.com/mkleehammer/pepperssh',
    cmdclass={'test': TestCommand}
)
