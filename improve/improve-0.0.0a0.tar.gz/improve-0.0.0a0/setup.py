# coding: UTF-8

from pathlib import Path
from setuptools import setup


BASE_DIR = Path(__file__).absolute().parent


def _get_long_description() -> str:
    with open(BASE_DIR / 'README.md', 'r') as readme:
        return readme.read()


setup(
    name='improve',
    version='0.0.0a0',
    description='Python utils',
    long_description=_get_long_description(),
    author='Wilbur Mayffair',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
    ],
)
