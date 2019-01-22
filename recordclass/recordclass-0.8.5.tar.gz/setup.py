# coding: utf-8

# The MIT License (MIT)
# 
# Copyright (c) <2011-2018> <Shibzukhov Zaur, szport at gmail dot com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import sys as _sys
_PY36 = _sys.version_info[:2] >= (3, 6)

from setuptools import setup
from setuptools.command.build_ext import build_ext
from setuptools.extension import Extension

use_cython = 0

if use_cython:
    from Cython.Distutils import Extension, build_ext
    from Cython.Compiler import Options
    Options.fast_fail = True

ext_modules = [
    Extension(
        "recordclass.memoryslots",
        ["lib/recordclass/memoryslots.c"]
    )]

if use_cython:
    ext_modules.append(Extension(
        "recordclass.dataobject",
        ["lib/recordclass/dataobject.pyx"]
    ))
else:
    ext_modules.append(Extension(
        "recordclass.dataobject",
        ["lib/recordclass/dataobject.c"]
    ))

description = """Mutable variants of tuple (memoryslots) and collections.namedtuple (recordclass), \
which support assignments and more memory saving variants (arrayclass and structclass)"""
    
with open('README.md') as f:
    long_description = f.read()

packages=['recordclass', 'recordclass.test']
if _PY36:
    packages.append('recordclass.test.typing')
    packages.append('recordclass.typing')

setup(
    name = 'recordclass',
    version = '0.8.5',
    description = description,
    author = 'Zaur Shibzukhov',
    author_email = 'szport@gmail.com',
    # maintainer = 'Zaur Shibzukhov',
    # maintainer_email = 'szport@gmail.com',
    license = "MIT License",
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules,
    package_dir = {'': 'lib'},
    packages = packages,
    url = 'http://intellimath.bitbucket.org/recordclass',
    download_url = 'https://bitbucket.org/intellimath/recordclass',
    long_description=long_description,
    long_description_content_type='text/markdown',
    platforms='Linux, Mac OS X, Windows',
    keywords=['namedtuple', 'recordclass', 'structclass', 'arrayclass'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
