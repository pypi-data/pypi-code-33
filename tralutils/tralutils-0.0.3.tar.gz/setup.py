#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os
import re

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="tralutils",
    version=find_version("tralutils", "__init__.py"),
    author='sv99',
    author_email='sv99@inbox.ru',
    url='https://github.com/sv99/tralutil',
    description='Utils for archive for video registrator Tral',
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires='>=3',
    platforms='any',
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'tralinfo = tralutils.tralinfo:main',
            'videodir = tralutils.videodir:main',
        ]
    },
    extras_require={
        'dev': [
            'twine',
        ]
    },
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ]
)