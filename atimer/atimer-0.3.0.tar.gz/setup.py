#!/usr/bin/env python
#
# atimer - timer library for asyncio
#
# Copyright (C) 2016-2019 by Artur Wroblewski <wrobell@riseup.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize

setup(
    name='atimer',
    packages=find_packages('.'),
    version='0.3.0',
    description='atimer - timer library for asyncio',
    author='Artur Wroblewski',
    author_email='wrobell@riseup.net',
    url='https://wrobell.dcmod.org/atimer',
    setup_requires = ['setuptools_git >= 1.0',],
    classifiers=[
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
    ],
    ext_modules=cythonize([
        Extension('atimer._atimer', ['atimer/_atimer.pyx'])
    ]),
    license='GPLv3+',
    long_description=open('README').read(),
)

# vim: sw=4:et:ai
