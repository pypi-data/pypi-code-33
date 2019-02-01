#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:copyright: (c) 2018 by Raul Gomis
:license: MIT, see LICENSE for more details.
"""
import io
import os

from setuptools import setup, find_packages, Command

# Package meta-data.
NAME = 'semversioner'
DESCRIPTION = 'Manage properly semver in your repository'
URL = 'https://github.com/raulgomis/semversioner'
EMAIL = 'raulgomis@gmail.com'
AUTHOR = 'Raul Gomis'
REQUIRES_PYTHON = '>=3.1.0'
VERSION = None

REQUIRED = [
    'click'
]

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, "README.md"), "rt", encoding="utf8") as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    with open(os.path.join(here, NAME, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.egg-info')


setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    tests_require=['nose'],
    url=URL,
    author=AUTHOR,
    author_email=EMAIL,
    license='MIT',
    packages=find_packages(exclude=('tests',)),
    python_requires=REQUIRES_PYTHON,

    entry_points={
        'console_scripts': [
            'semversioner = semversioner:main'
        ]
    },

    install_requires=REQUIRED,

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Environment :: Console',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',

        'Operating System :: OS Independent',
    ],

    cmdclass={
        'clean': CleanCommand,
    }
)