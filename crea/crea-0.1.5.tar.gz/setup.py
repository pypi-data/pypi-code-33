# -*- coding: utf-8 -*-
"""Packaging logic for crea."""
import codecs
import io
import os
import sys

from setuptools import setup

# Work around mbcs bug in distutils.
# http://bugs.python.org/issue10945

try:
    codecs.lookup('mbcs')
except LookupError:
    ascii = codecs.lookup('ascii')
    codecs.register(lambda name, enc=ascii: {True: enc}.get(name == 'mbcs'))

VERSION = '0.1.5'

tests_require = ['mock >= 2.0.0', 'pytest', 'pytest-mock', 'parameterized']

requires = [
    "future",
    "ecdsa",
    "requests",
    "websocket-client",
    "appdirs",
    "Events",
    "scrypt",
    "pylibscrypt",
    "pycryptodomex",
    "pytz",
    "Click",
    "prettytable",
    "pyyaml"
]


def write_version_py(filename):
    """Write version."""
    cnt = """\"""THIS FILE IS GENERATED FROM crea SETUP.PY.\"""
version = '%(version)s'
"""
    with open(filename, 'w') as a:
        a.write(cnt % {'version': VERSION})


def get_long_description():
    """Generate a long description from the README file."""
    descr = []
    for fname in ('README.rst',):
        with io.open(fname, encoding='utf-8') as f:
            descr.append(f.read())
    return '\n\n'.join(descr)


if __name__ == '__main__':

    # Rewrite the version file everytime
    write_version_py('crea/version.py')
    write_version_py('creabase/version.py')
    write_version_py('creaapi/version.py')
    write_version_py('creagraphenebase/version.py')

    setup(
        name='crea',
        version=VERSION,
        description='Unofficial Python library for CREA',
        long_description=get_long_description(),
        download_url='https://github.com/creativechain/crea-python-lib/tarball/' + VERSION,
        author='Creativechain Foundation',
        author_email='info@creativechain.org',
        maintainer='Creativechain Foundation',
        maintainer_email='info@creativechain.org',
        url='https://github.com/creativechain/crea-python-lib',
        keywords=['crea', 'library', 'api', 'rpc'],
        packages=[
            "crea",
            "creaapi",
            "creabase",
            "creagraphenebase",
            "creagrapheneapi"
        ],
        classifiers=[
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Intended Audience :: Financial and Insurance Industry',
            'Topic :: Office/Business :: Financial',
        ],
        install_requires=requires,
        entry_points={
            'console_scripts': [
                'creapy=crea.cli:cli',
            ],
        },
        setup_requires=['pytest-runner'],
        tests_require=tests_require,
        include_package_data=True,
    )
