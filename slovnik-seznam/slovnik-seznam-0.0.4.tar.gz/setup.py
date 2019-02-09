#!/usr/bin/env python3
import os.path

from setuptools import setup

def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as inf:
        return "\n" + inf.read().replace("\r\n", "\n")

setup(
    name='slovnik-seznam',
    version="0.0.4",
    description='Translate from/to Czech language',
    author='Matěj Cepl',
    author_email='mcepl@cepl.eu',
    url='https://gitlab.com/mcepl/slovnik-seznam.git',
    py_modules=['slovnik'],
    long_description=read('README.rst'),
    entry_points={
        'console_scripts': [
            'slovnik=slovnik:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
    ],
    install_requires=['html2text', 'beautifulsoup4'],
)
