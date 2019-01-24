#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

extras_require = {
    'voice': ['PyNaCl==1.0.1'],
}

classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
]

setup(
    name            = 'discord',
    version         = '0.16.12',
    author          = 'Philip Howard',
    author_email    = 'phil@gadgetoid.com',
    description     = """Wrapper for discord.py""",
    long_description= "",
    license         = 'MIT',
    keywords        = 'Discord',
    url             = 'https://pypi.python.org/pypi/discord.py',
    classifiers     = classifiers,
    py_modules      = [],
    install_requires= [ 'discord.py==0.16.12' ],
    extras_require=extras_require,
)
