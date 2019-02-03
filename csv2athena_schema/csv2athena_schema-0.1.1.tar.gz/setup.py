# -*- coding: utf-8 -*-
import re
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand


REQUIRES = [
    'docopt',
]

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


def find_version(fname):
    '''Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    '''
    version = ''
    with open(fname, 'r') as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError('Cannot find version information')
    return version

__version__ = find_version("csv2athena_schema.py")


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content

setup(
    name='csv2athena_schema',
    version="0.1.1",
    description='A Python Script to build a athena create table from csv file',
    long_description=read("README.rst"),
    author='Yukihiro Okada',
    author_email='callistoiv+pypi@gmail.com',
    url='https://github.com/yuokada/csv2athena_schema',
    install_requires=REQUIRES,
    license=read("LICENSE"),
    zip_safe=False,
    keywords='csv2athena_schema',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    py_modules=["csv2athena_schema"],
    entry_points={
        'console_scripts': [
            "csv2athena_schema = csv2athena_schema:main"
        ]
    },
    tests_require=['pytest', 'coverage', 'coveralls'],
    cmdclass={'test': PyTest}
)
